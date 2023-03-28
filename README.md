# atstk

```sql
CREATE TABLE STOCK_ORDER(
   id          int        PRIMARY KEY NOT NULL,
   stock_id    VARCHAR(4) NOT NULL,
   lot_num     int        NOT NULL,
   type        VARCHAR(10) NOT NULL,
   price_type  VARCHAR(10) NOT NULL,
   price       float      NOT NULL,
   status      VARCHAR(10) NOT NULL,
   create_time timestamp  NOT NULL,
   update_time timestamp  NOT NULL
);
```

```sql
CREATE TABLE HEALTH_CHECK(
   name            VARCHAR(10)  NOT NULL,
   last_check_time timestamp    NOT NULL
);
```

```sql
INSERT INTO HEALTH_CHECK
VALUES ('Agent', CURRENT_TIMESTAMP);
```
