def generate_html_filename(event_id):
    """
    Break out for clarity
    """
    return f"{event_id}.html"


def generate_report_dir(output_dir: str, eventTime) -> str:
    """
    Generate path for the report -- just the directory,
    not the filename itself.  No trailing slash.

    Parameters:
    config: config dictionary
    event_date: date of the event
    """
    return output_dir + "/" + eventTime.strftime("%Y/%m/%d")


def generate_report_url(event_id, eventTime) -> str:
    """
    Generate URL for report
    """
    filename = generate_html_filename(event_id)
    html_path = eventTime.strftime("%Y/%m/%d")
    return f"https://home.saintaardvarkthecarpeted.com/earthquake_data/{html_path}/{filename}"
