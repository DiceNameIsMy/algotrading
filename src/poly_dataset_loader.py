from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

import pandas as pd

import sqlite3
from py_clob_client.client import BookParams


@dataclass
class TokenTable:
    token: str
    market_id: str
    token_type: str


@dataclass
class OrderItem:
    token: str
    price: float
    size: float


def load_and_store_order_book(markets: list[str]):
    tokens, timestamp, asks, bids = load_order_book(markets)

    store_data(tokens, timestamp, asks, bids)


def load_order_book(markets: list[str]):
    markets_body = [poly_client.get_market(m) for m in markets]

    # Get tokens
    tokens: list[TokenTable] = []
    for market in markets_body:
        for token in market["tokens"]:
            tokens.append(
                TokenTable(token["token_id"], market["condition_id"], token["outcome"])
            )

    # Get order books of tokens
    timestamp = datetime.now()
    order_books = poly_client.get_order_books([BookParams(t.token) for t in tokens])

    # Transform them

    # Will contain: token_id, price, size
    asks: list[OrderItem] = []
    bids: list[OrderItem] = []
    for order_book in order_books:
        sorted_asks = sorted(order_book.asks, key=lambda x: x.price)
        min_3_asks = sorted_asks[0 : min(3, len(order_book.asks))]
        for ask in min_3_asks:
            asks.append(OrderItem(order_book.asset_id, ask.price, ask.size))

        sorted_bids = sorted(order_book.bids, key=lambda x: x.price)
        max_3_bids = sorted_bids[-min(3, len(order_book.bids)) :]
        for bid in max_3_bids:
            bids.append(OrderItem(order_book.asset_id, bid.price, bid.size))

    return tokens, timestamp, asks, bids


def get_database_dir() -> str:
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def store_data(
    tokens: list[TokenTable],
    timestamp: datetime,
    asks: list[OrderItem],
    bids: list[OrderItem],
):
    db_dir = get_database_dir()
    conn = sqlite3.connect(db_dir / "order_book.db")
    try:
        cursor = conn.cursor()
        create_tables(cursor)

        # Insert tokens
        cursor.executemany(
            "INSERT OR IGNORE INTO token (token, market_id, token_type) VALUES (?, ?, ?)",
            [(t.token, t.market_id, t.token_type) for t in tokens],
        )
        conn.commit()

        token_ids_table = cursor.execute(
            "SELECT t.token_id, t.token FROM token t"
        ).fetchall()
        token_ids = {t[1]: t[0] for t in token_ids_table}  # token -> token_id

        # Insert token timeseries
        timeseries_ids: dict[str, int] = {}  # token_id -> timeseries_id
        for _, token_id in token_ids.items():
            cursor.execute(
                """
                INSERT INTO token_timeseries (timestamp, token_id) VALUES (?, ?)
                """,
                (timestamp.isoformat(), token_id),
            )
            timeseries_ids[token_id] = cursor.lastrowid
        conn.commit()

        # Insert asks and bids
        cursor.executemany(
            "INSERT INTO bids (timeseries_id, price, size) VALUES (?, ?, ?)",
            [(timeseries_ids[token_ids[b.token]], b.price, b.size) for b in bids],
        )
        cursor.executemany(
            "INSERT INTO asks (timeseries_id, price, size) VALUES (?, ?, ?)",
            [(timeseries_ids[token_ids[a.token]], a.price, a.size) for a in asks],
        )
        conn.commit()

    finally:
        conn.close()

    return True


def create_tables(cursor: sqlite3.Cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS token (
            token_id INTEGER PRIMARY KEY,
            token VARCHAR(80) NOT NULL,
            market_id VARCHAR(80) NOT NULL,
            token_type VARCHAR(10) NOT NULL CHECK (token_type IN ('Yes', 'No')),
            UNIQUE(token, market_id, token_type)
        );
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS token_timeseries (
            timeseries_id INTEGER PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            token_id INTEGER NOT NULL REFERENCES token(token_id) ON DELETE CASCADE
        );
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bids (
            bid_id INTEGER PRIMARY KEY,
            timeseries_id INTEGER NOT NULL REFERENCES token_timeseries(timeseries_id) ON DELETE CASCADE,
            price DECIMAL(20, 8) NOT NULL,
            size DECIMAL(20, 8) NOT NULL
        );
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS asks (
            ask_id INTEGER PRIMARY KEY,
            timeseries_id INTEGER NOT NULL REFERENCES token_timeseries(timeseries_id) ON DELETE CASCADE,
            price DECIMAL(20, 8) NOT NULL,
            size DECIMAL(20, 8) NOT NULL
        );
    """
    )

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_asks_timeseries_id ON asks (timeseries_id);"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_bids_timeseries_id ON bids (timeseries_id);"
    )


def query_token_timeseries_by_tokens(tokens: list[str]):
    db_dir = get_database_dir()
    conn = sqlite3.connect(db_dir / "order_book.db")

    try:
        cursor = conn.cursor()

        query = """
        SELECT tt.timeseries_id, tt.timestamp, tt.token_id
        FROM token_timeseries tt
        JOIN token t ON tt.token_id = t.token_id
        WHERE t.token IN ({})
        """.format(
            ",".join("?" for _ in tokens)
        )

        cursor.execute(query, tokens)
        result = cursor.fetchall()

        return result
    finally:
        conn.close()


def query_asks_and_bids_by_timeseries(timeseries_id: int, cursor: sqlite3.Cursor):
    # Query asks
    asks_query = """
    SELECT price, size, timeseries_id
    FROM asks
    WHERE timeseries_id = ?
    """
    cursor.execute(asks_query, (timeseries_id,))
    asks = cursor.fetchall()

    # Query bids
    bids_query = """
    SELECT price, size, timeseries_id
    FROM bids
    WHERE timeseries_id = ?
    """
    cursor.execute(bids_query, (timeseries_id,))
    bids = cursor.fetchall()

    return asks, bids


def load_asks_and_bids_for_timeseries(timeseries_ids: list[int]):
    data = {}

    db_dir = get_database_dir()
    conn = sqlite3.connect(db_dir / "order_book.db")

    try:
        cursor = conn.cursor()

        for timeseries_id in timeseries_ids:
            asks, bids = query_asks_and_bids_by_timeseries(timeseries_id, cursor)
            data[timeseries_id] = {
                "ask_max": max(asks + [(0, None, None)], key=lambda x: x[0])[0],
                "bid_min": min(bids + [(float("inf"), None, None)], key=lambda x: x[0])[0],
            }
    finally:
        conn.close()

    df = pd.DataFrame.from_dict(data, orient="index")
    return df


if __name__ == "__main__":
    markets = [
        "0x0cedbcc216d551bbb704f18cbad8932ea427139760e3dcf715c4a134c875474e",
        "0x15dbb75d18291f1341ef0d33328a3bcc72cc0872b4dd478a9ce9b00b6dd9dd2c",
        "0x2118aa01cc2345896b160331291cf0e1d4146da1d9413f1aa214ffbdd0134937",
        "0x2dded342861dd48b5a239c51a9b7b1cfee20cb1641c875eec3388807cea843b8",
        "0x453157d57aa34741278cb3d6f20d3d01b138395c3ae9eb34e2b97137fe0f2eaa",
        "0x62157086c05e1f5ae7c72ae72c0c1fe62cf4d0b045ceefc18357802bcd005ef8",
        "0x7a18e4d613d7bf6afa06aa9eb1f9287ca81e841d77ae6d5fabdab37f0c0b5d6c",
        "0x9d84821a6c8b45fcd9dad9f50f1b0fc6cb76de7a68d7686bfefba697c32a6375",
        "0xa356cb30609f25eab2219e0aeeb64f9e5de471213427ff911264892a205e1c57",
        "0xad172e84e2a01b30406245a32cade80ad56eb6941ed9e5b22c73b1b206dc7e11",
        "0xc9501eac519c7b631d0425ea093a127f4552ad52b8fdf4e591cea89b31aad981",
        "0xedf6eed432b16b5473929350ee322fed560a4ba4a70785ed06331eac724e7826",
        "0xef3446eac0c8baefadf48c8007429643bdb3d81fbcee4074395600cc40a7c682",
        "0xf9d0a1390e11c9119cf084b3b86bd883052932a951bf933cf23bdd1c0700bebd",
    ]
    try:
        from poly_api import poly_client

        load_and_store_order_book(markets)
    except Exception as e:
        print(f"Script execution at {datetime.now().isoformat()} completed with error.")
        raise e
