"""Supabase queries: one immutable result per quiz and a fresh top 20."""
from supabase import create_client
from postgrest.exceptions import APIError


def connect(url, key):
    return create_client(url, key)


def save_result(client, result):
    try:
        client.table("results").insert(result, returning="minimal").execute()
    except APIError as error:
        # A lost response may cause a retry after the INSERT already succeeded.
        if error.code != "23505":
            raise
        rows = (client.table("results").select("id,name,correct_answers,elapsed_seconds")
                .eq("id", result["id"]).execute().data)
        if not rows or any(rows[0].get(key) != value for key, value in result.items()):
            raise


def fetch_leaderboard(client):
    return (client.table("results")
            .select("name,correct_answers,elapsed_seconds")
            .order("correct_answers", desc=True)
            .order("elapsed_seconds")
            .order("created_at")
            .order("id")
            .limit(20).execute().data)
