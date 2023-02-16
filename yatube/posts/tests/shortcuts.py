from posts.models import Post, Group

def post_create(text, user, group):
    return Post.objects.create(text=text, author=user, group=group)


def group_create(title, description):
    return Group.objects.create(
        title=title,
        slug='slug',
        description=description,
    )
