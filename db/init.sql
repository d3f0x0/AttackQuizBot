DROP TABLE IF EXISTS public.techniques CASCADE;
CREATE TABLE public.techniques
(
    id_ta            varchar       NOT NULL,
    name             varchar       NOT NULL,
    description      varchar       NOT NULL,
    id_tactics       varchar       NOT NULL,
    PRIMARY KEY (id_ta, name, id_tactics)
);

DROP TABLE IF EXISTS public.tactics CASCADE;
CREATE TABLE public.tactics
(
    id_t             varchar       NOT NULL,
    name             varchar       NOT NULL,
    description      varchar       NOT NULL,
    PRIMARY KEY (id_t, name)
);

DROP TABLE IF EXISTS public.mitigations CASCADE;
CREATE TABLE public.mitigations
(
    id_mt            varchar       NOT NULL,
    name             varchar       NOT NULL,
    description      varchar       NOT NULL,
    id_tech          varchar       NOT NULL,
    PRIMARY KEY (id_mt, name, id_tech)
);

DROP TABLE IF EXISTS public.users CASCADE;
CREATE TABLE public.users
(
    id_user   int8      NOT NULL,
    name      varchar     NOT NULL,
    last_date timestamp   NOT NULL,
    PRIMARY KEY (id_user, name)
);

DROP TABLE IF EXISTS public.statistics CASCADE;
CREATE TABLE public.statistics
(
    id_user                int8      NOT NULL,
    mitre_id               varchar   NOT NULL,
    true_answers           int8      DEFAULT 0,
    true_poll_answer       int8      NOT NULL,
    count                  int8      DEFAULT 0,
    poll_id                int8      NOT NULL,
    PRIMARY KEY (id_user, mitre_id)
);

COMMENT ON COLUMN statistics.id_user is 'Telegram user id';
COMMENT ON COLUMN statistics.mitre_id is 'Mitre ID';
COMMENT ON COLUMN statistics.true_answers is 'Count true answers';
COMMENT ON COLUMN statistics.true_poll_answer is 'True answer on poll';
COMMENT ON COLUMN statistics.count is 'Count poll answers';
COMMENT ON COLUMN statistics.poll_id is 'Poll id';

