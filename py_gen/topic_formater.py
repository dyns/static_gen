def format_topic_anchor_tag(topics_slug, topic_title):
    formatted_topic_name = topic_title.lower().replace(' ', '_')
    topic_path = '{topics_slug}/{slug}'.format(topics_slug=topics_slug, slug=formatted_topic_name)
    anchor_tag = '<a href="/{topic_path}">{topic_title}</a>'.format(topic_path=topic_path, topic_title=topic_title)
    return (topic_path, anchor_tag)

def generate_topic_pages_links(topics_slug, post_topics):
    topic_links = []
    anchor_tags = []

    for topic_title in post_topics:
        (topic_path, anchor_tag) = format_topic_anchor_tag(topics_slug, topic_title)
        topic_links.append(topic_path)
        anchor_tags.append(anchor_tag)

    return (topic_links, anchor_tags)