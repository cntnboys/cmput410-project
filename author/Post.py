
class Post(object):
    """Creates Post object"""  
    def __init__(self,title, post_id, post_uuid, author_id, content, image, privacy, date):
        self.title = title
        self.post_id = post_id
        self.post_uuid = post_uuid
        self.author_id = author_id
        self.content = content
        self.image = image
        self.privacy = privacy
        self.date = date
      
