--
-- PostgreSQL database dump
--

\restrict OW8A2sBx1IYzy8A0SdD6cofjPlsxYfbODCXpdkKpp0tgTCNwsbaVeeVt9m53Dta

-- Dumped from database version 15.14 (Debian 15.14-1.pgdg13+1)
-- Dumped by pg_dump version 15.14 (Debian 15.14-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: document_relations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.document_relations (
    id uuid NOT NULL,
    source_doc_id uuid,
    target_doc_id uuid,
    relation_type character varying(100),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.document_relations OWNER TO postgres;

--
-- Name: documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.documents (
    id uuid NOT NULL,
    type character varying(50) NOT NULL,
    title character varying(500) NOT NULL,
    content text NOT NULL,
    metadata jsonb NOT NULL,
    source character varying(500),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.documents OWNER TO postgres;

--
-- Name: embeddings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.embeddings (
    id uuid NOT NULL,
    document_id uuid,
    embedding_vector jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.embeddings OWNER TO postgres;

--
-- Data for Name: document_relations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.document_relations (id, source_doc_id, target_doc_id, relation_type, created_at) FROM stdin;
\.


--
-- Data for Name: documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.documents (id, type, title, content, metadata, source, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: embeddings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.embeddings (id, document_id, embedding_vector, created_at) FROM stdin;
\.


--
-- Name: document_relations document_relations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_relations
    ADD CONSTRAINT document_relations_pkey PRIMARY KEY (id);


--
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);


--
-- Name: embeddings embeddings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.embeddings
    ADD CONSTRAINT embeddings_pkey PRIMARY KEY (id);


--
-- Name: idx_documents_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_documents_created_at ON public.documents USING btree (created_at);


--
-- Name: idx_documents_metadata; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_documents_metadata ON public.documents USING gin (metadata);


--
-- Name: idx_documents_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_documents_type ON public.documents USING btree (type);


--
-- Name: document_relations document_relations_source_doc_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_relations
    ADD CONSTRAINT document_relations_source_doc_id_fkey FOREIGN KEY (source_doc_id) REFERENCES public.documents(id);


--
-- Name: document_relations document_relations_target_doc_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.document_relations
    ADD CONSTRAINT document_relations_target_doc_id_fkey FOREIGN KEY (target_doc_id) REFERENCES public.documents(id);


--
-- Name: embeddings embeddings_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.embeddings
    ADD CONSTRAINT embeddings_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id);


--
-- PostgreSQL database dump complete
--

\unrestrict OW8A2sBx1IYzy8A0SdD6cofjPlsxYfbODCXpdkKpp0tgTCNwsbaVeeVt9m53Dta

