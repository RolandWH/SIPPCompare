import os
import sqlite3


class DBHandler:
    def __init__(self):
        def create_tables():
            self.cur.execute("""
                CREATE TABLE "tblPlatforms" (
                    "PlatformID"	INTEGER NOT NULL UNIQUE,
                    "PlatformName"	TEXT NOT NULL,
                    PRIMARY KEY("PlatformID")
                )
            """)

            self.cur.execute("""
                CREATE TABLE "tblFlatPlatFees" (
                    "PlatformID"	INTEGER NOT NULL,
                    "SharePlatFee"	REAL NOT NULL,
                    "SharePlatMaxFee"	REAL,
                    PRIMARY KEY("PlatformID"),
                    FOREIGN KEY("PlatformID") REFERENCES "tblPlatforms"("PlatformID")
                )
            """)

            self.cur.execute("""
                CREATE TABLE "tblFlatDealFees" (
                    "PlatformID"	INTEGER NOT NULL,
                    "FundDealFee"	REAL,
                    "ShareDealFee"	REAL NOT NULL,
                    "ShareDealReduceTrades"	REAL,
                    "ShareDealReduceAmount"	REAL,
                    PRIMARY KEY("PlatformID"),
                    FOREIGN KEY("PlatformID") REFERENCES "tblPlatforms"("PlatformID")
                )
            """)

            self.cur.execute("""
                CREATE TABLE "tblFundPlatFee" (
                    "PlatformID"	INTEGER NOT NULL,
                    "Band"	REAL NOT NULL,
                    "Fee"	REAL NOT NULL,
                    PRIMARY KEY("PlatformID","Band","Fee"),
                    FOREIGN KEY("PlatformID") REFERENCES "tblPlatforms"("PlatformID")
                )
            """)

            self.cur.execute("""
                CREATE TABLE "tblUserDetails" (
                    "PensionValue"	REAL,
                    "SliderValue"	INTEGER,
                    "ShareTrades"	INTEGER,
                    "FundTrades"	INTEGER
                )
            """)

        if not os.path.exists("SIPPCompare.db"):
            db_exists = False
        else:
            db_exists = True

        self.conn = sqlite3.connect("SIPPCompare.db")
        self.cur = self.conn.cursor()
        if not db_exists:
            create_tables()

    def retrieve_plat_list(self) -> list:
        res = self.cur.execute("SELECT PlatformName FROM tblPlatforms")
        res_list = res.fetchall()
        plat_name_list = []
        for platform in res_list:
            plat_name_list.append(platform[0])

        return plat_name_list

    def write_user_details(self, pension_val: float, slider_val: int, share_trades: int, fund_trades: int):
        user_details_data = (pension_val, slider_val, share_trades, fund_trades)

        res = self.cur.execute("SELECT EXISTS(SELECT 1 FROM tblUserDetails)").fetchone()
        if res[0] == 0:
            self.cur.execute("INSERT INTO tblUserDetails VALUES (?, ?, ?, ?)", user_details_data)
        else:
            self.cur.execute("""
                UPDATE tblUserDetails SET 
                PensionValue = ?,
                SliderValue = ?,
                ShareTrades = ?,
                FundTrades = ?
            """, user_details_data)
        self.conn.commit()

    def retrieve_user_details(self) -> dict:
        res = self.cur.execute("SELECT EXISTS(SELECT 1 FROM tblUserDetails)").fetchone()
        if res[0] == 0:
            return {"NO_RECORD": None}

        res = self.cur.execute("SELECT * FROM tblUserDetails")
        res_tuple = res.fetchone()
        user_details_dict = {
            "pension_val":  res_tuple[0],
            "slider_val":   res_tuple[1],
            "share_trades": res_tuple[2],
            "fund_trades":  res_tuple[3]
        }

        return user_details_dict
