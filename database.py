from sqlalchemy import create_engine,text

engine = create_engine(
    "postgresql+psycopg2://root:bth63051zF4pptj6ytBjVofIewGkupaZ@dpg-csseg29u0jms73ea4kf0-a.oregon-postgres.render.com/dma_app?sslmode=require"
)

def add_product_to_db(data,username,uid):

    with engine.connect() as conn:
        query = text(
            "INSERT INTO products(fname, fid, pname, quantity, price, dt) "
            "VALUES(:fname, :fid, :pname, :quantity, :price, :dt)"
        )
        conn.execute(
            query,
            {
                "fname": username,
                "fid": uid,
                "pname": data["pname"],
                "quantity": data["quantity"],
                "price": data["price"],
                "dt": data["date"],
            },
        )
        conn.commit()

