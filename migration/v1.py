############################################################
#          Migration V1
#
# Due to the bad design of old database schema, it becomes
# very difficult to maintain different document type. It
# requires consistent naming convention.
#
# In this script, the old data is retrived from production
# dataset, and migrated to dev dataset, and later on migrate
# back to production with conssitent naaming convention.
############################################################
# %%
from word2json.service import Services

service = Services.parse_file("credential.json")
sanity = service.sanity.get_client(dev=False)
sanity_dev = service.sanity.get_client(dev=True)
# %% 暖曦话语


def find_author(ref, targets):
    author = filter(lambda x: x["_id"] == ref, targets)
    return list(author)[0]["name"]


authors = sanity.get("*[_type=='author']")
posts = sanity.get("*[_type=='post']")
new_posts = []
for post in posts:
    new_post = {
        "title": post["title"],
        "slug": post["slug"],
        "author": find_author(post["author"]["_ref"], authors),
        "mainImageUrl": post["mainImageUrl"],
        "featured": post.get("featured", None),
        "category": post["category"],
        "tags": post.get("tags", []),
        "publishedAt": post["publishedAt"],
        "writtenAt": post["writtenAt"],
        "description": post["description"],
        "body": post["body"],
        "articleUrls": [],
    }
    private = {}
    for pfield in ["_createdAt", "_id", "_rev", "_type", "_updatedAt"]:
        private[pfield] = post[pfield]
    new_post.update(private)
    new_posts.append(new_post)
res = sanity_dev.insert(new_posts)
print(len(res.json()["results"]), "posts uploaded")
# %% 观者评说


def process_article(related):
    if len(related) == 0:
        return []
    payloads = []
    for article in related:
        payload = {
            "_key": article["_key"],
            "_type": "articleUrlObject",
            "urlTitle": article["title"],
            "urlField": article["urlField"],
        }
        payloads.append(payload)
    return payloads


voices = sanity.get("*[_type=='voice']")
new_posts = []
for post in voices:
    new_post = {
        "title": post["title"],
        "slug": post["slug"],
        "author": find_author(post["author"]["_ref"]),
        "mainImageUrl": post["mainImageUrl"],
        "featured": post.get("featured", None),
        "category": post["category"],
        "tags": post.get("tags", []),
        "publishedAt": post["publishedAt"],
        "writtenAt": post["writtenAt"],
        "description": post["description"],
        "body": post["body"],
        "articleUrls": process_article(post.get("related", [])),
    }
    private = {}
    for pfield in ["_createdAt", "_id", "_rev", "_type", "_updatedAt"]:
        private[pfield] = post[pfield]
    new_post.update(private)
    new_posts.append(new_post)
res = sanity_dev.insert(new_posts)
print(len(res.json()["results"]), "voices uploaded")

# %% 部分卷宗


def process_images(images):
    if len(images) == 0:
        return []
    payloads = []
    for iamge in images:
        payload = {
            "_key": iamge["_key"],
            "_type": "imageUrlObject",
            "urlTitle": iamge["url_title"],
            "urlField": iamge["urlField"],
            "height": iamge.get("height", None),
            "width": iamge.get("width", None),
        }
        payloads.append(payload)
    return payloads


casefiles = sanity.get("*[_type=='casefiles']")
new_posts = []
for post in casefiles:
    new_post = {
        "_type": "casefile",
        "title": post["title"],
        "description": post["description"],
        "header": post.get("header", None),
        "slug": post["slug"],
        "order": post["order"],
        "tags": post.get("tags", []),
        "featured": post.get("featured", None),
        "mainImageUrl": post["mainImageUrl"],
        "articleUrls": process_article(post.get("related", [])),
        "imageUrls": process_images(post.get("image_urls", [])),
        "category": post["classification"],
        "publishedAt": post["publishedAt"],
        "writtenAt": post["writtenAt"],
        "body": post["body"],
    }
    private = {}
    for pfield in ["_createdAt", "_id", "_rev", "_updatedAt"]:
        private[pfield] = post[pfield]
    new_post.update(private)
    new_posts.append(new_post)
res = sanity_dev.insert(new_posts)
print(len(res.json()["results"]), "casefiles uploaded")

# %% 时间线


def find_people(people, targets):
    ret = []
    for p in people:
        ret.append(find_author(p["_ref"], targets))
    return ret


timelines = sanity.get("*[_type=='timeline']")
peoples = sanity.get("*[_type=='people']")

new_posts = []
for post in timelines:
    new_post = {
        "title": post["title"],
        "date": post["date"],
        "time": post.get("time", None),
        "order": post["order"],
        "people": find_people(post["people"], peoples),
        "source": post.get("source", None),
        "articleUrls": process_article(post.get("related", [])),
        "imageUrls": process_images(post.get("image_urls", [])),
        "category": post["type"],
        "tags": post.get("tags", []),
    }
    private = {}
    for pfield in ["_createdAt", "_id", "_rev", "_type", "_updatedAt"]:
        private[pfield] = post[pfield]
    new_post.update(private)
    if post.get("event", None) is not None:
        new_post["body"] = post.get("event")

    new_posts.append(new_post)
res = sanity_dev.insert(new_posts)
print(len(res.json()["results"]), "timelines uploaded")
# %% 谣言澄清


def process_article_fix(related):
    if len(related) == 0:
        return []
    payloads = []
    for article in related:
        payload = {
            "_key": article["_key"],
            "_type": "articleUrlObject",
            "urlTitle": article["url_title"],
            "urlField": article["urlField"],
        }
        payloads.append(payload)
    return payloads


rumors = sanity.get("*[_type=='rumor']")
new_posts = []
for post in rumors:
    new_post = {
        "title": post["question"],
        "importance": post.get("importance", None),
        "author": post.get("author", None),
        "rumorSpreader": post.get("rumor_spreader", []),
        "rumorVictim": post.get("rumor_victim", []),
        "rumor": post.get("rumor", None),
        "truth": post.get("truth", None),
        "tags": post.get("tags", []),
        "rumorImageUrls": process_images(post.get("rumor_images", [])),
        "truthImageUrls": process_images(post.get("truth_images", [])),
        "rumorArticleUrls": process_article_fix(post.get("rumor_posts", [])),
        "truthArticleUrls": process_article_fix(post.get("truth_posts", [])),
    }
    private = {}
    for pfield in ["_createdAt", "_id", "_rev", "_type", "_updatedAt"]:
        private[pfield] = post[pfield]
    new_post.update(private)
    new_posts.append(new_post)
res = sanity_dev.insert(new_posts)
print(len(res.json()["results"]), "rumors uploaded")

# %% 关于我们

abouts = sanity.get("*[_type=='about']")
new_posts = []
for post in abouts:
    new_post = {
        "title": post["title"],
        "subtitle": post.get("subtitle", None),
        "quote": post.get("quote", None),
        "slug": post.get("slug", None),
        "mainImageUrl": post.get("imageUrl", None),
        "body": post.get("content", None),
        "footer": post.get("footer", []),
    }
    private = {}
    for pfield in ["_createdAt", "_id", "_rev", "_type", "_updatedAt"]:
        private[pfield] = post[pfield]
    new_post.update(private)
    new_posts.append(new_post)
res = sanity_dev.insert(new_posts)
print(len(res.json()["results"]), "abouts uploaded")

# %% 影音资料

medias = sanity.get("*[_type=='media']")
# %%
new_posts = []
for post in medias:
    new_post = {
        "title": post["title"],
        "subtitle": post.get("subtitle", None),
        "slug": post.get("slug", None),
        "author": post.get("author", None),
        "mediaUrl": post.get("mediaUrl", None),
        "category": post.get("category", None),
        "tags": post.get("tags", []),
        "mainImageUrl": post.get("imageUrl", None),
        "description": post.get("description", None),
        "publishedAt": post.get("publishedAt", None),
        "writtenAt": post.get("writtenAt", None),
        "downloadLink": post.get("download_link", None),
        "downloadMeta": post.get("download_meta", None),
    }
    private = {}
    for pfield in ["_createdAt", "_id", "_rev", "_type", "_updatedAt"]:
        private[pfield] = post[pfield]
    new_post.update(private)
    if post.get("content", None) is not None:
        new_post["body"] = post.get("content")

    new_posts.append(new_post)
res = sanity_dev.insert(new_posts)
print(len(res.json()["results"]), "medias uploaded")
