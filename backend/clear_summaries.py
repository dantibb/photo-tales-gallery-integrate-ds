from tinydb import TinyDB, Query

def clear_all_summaries():
    db = TinyDB('local_contexts.json')
    for item in db:
        db.update({
            'summary': '',
            'summary_title': '',
            'summary_summary': ''
        }, Query().image_name == item['image_name'])
    print("All summaries cleared.")

if __name__ == "__main__":
    clear_all_summaries() 