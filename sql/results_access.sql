-- Run in Supabase SQL Editor after creating public.results.
BEGIN;
ALTER TABLE public.results ENABLE ROW LEVEL SECURITY;
GRANT USAGE ON SCHEMA public TO anon;
REVOKE ALL ON TABLE public.results FROM anon, authenticated;
GRANT SELECT, INSERT ON TABLE public.results TO anon;

DROP POLICY IF EXISTS results_read ON public.results;
CREATE POLICY results_read ON public.results
    FOR SELECT TO anon USING (true);

DROP POLICY IF EXISTS results_insert ON public.results;
CREATE POLICY results_insert ON public.results
    FOR INSERT TO anon WITH CHECK (true);

CREATE INDEX IF NOT EXISTS results_leaderboard_idx
    ON public.results (correct_answers DESC, elapsed_seconds ASC, created_at ASC, id ASC);
COMMIT;
