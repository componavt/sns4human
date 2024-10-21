def get_all_posts(token, version, domain):
  offset=0
  all_posts = []
  while True:
    responce = requests.get('https://api.vk.com/method/wall.get',
                        params={
                            'access_token' : token,
                            'v': version,
                            'domain': domain,
                            'offset': offset,
                            'count': 100
                        })
    data = responce.json()
    if 'response' in data:
        posts = data['response']['items']
        all_posts.extend(posts)
        if len(posts) < 100:
            return all_posts
        offset += 100
    else:
        return
    
def create_all_posts_csv(token, version, domain):
  posts = get_all_posts(token, version, domain)
  df = pd.DataFrame(posts)

  df['likes'] = df['likes'].fillna({'count': 0})
  df['reposts'] = df['reposts'].fillna({'count': 0})
  df['views'] = df['views'].fillna({'count': 0})

  df = df[['id','text', 'date', 'likes','reposts','views']]
  df['date'] = pd.to_datetime(df['date'], unit='s')

  df['likes'] = df['likes'].apply(lambda x: int(x['count']) if isinstance(x, dict) else 0)
  df['reposts'] = df['reposts'].apply(lambda x: int(x['count']) if isinstance(x, dict) else 0)
  df['views'] = df['views'].apply(lambda x: int(x['count']) if isinstance(x, dict) else 0)

  df['text'] = df['text'].str.replace('\n', ' ', regex=False)
  df['date'] = df['date'].dt.tz_localize('UTC').dt.tz_convert('Europe/Moscow')
  df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')

  name = domain + "_all_posts.csv"
  df.to_csv(name, index=False)

def get_vk_posts_with_comments(domain, access_token, count=100):
    posts_url = 'https://api.vk.com/method/wall.get'
    comments_url = 'https://api.vk.com/method/wall.getComments'

    posts = []
    offset = 0

    while True:
        response = requests.get(posts_url, params={
            'domain': domain,
            'count': count,
            'offset': offset,
            'access_token': access_token,
            'v': '5.131'
        }).json()

        if 'response' not in response:
            print("Ошибка при получении постов:", response)
            break

        posts_batch = response['response']['items']
        if not posts_batch:
            break

        for post in posts_batch:
            post_id = post['id']
            owner_id = post['owner_id']


            comments_response = requests.get(comments_url, params={
                'owner_id': owner_id,
                'post_id': post_id,
                'access_token': access_token,
                'v': '5.131'
            }).json()

            if 'response' in comments_response:
                comments = comments_response['response'].get('items', [])
                post['comments'] = comments
            else:
                print("Ошибка при получении комментариев:", comments_response)

            posts.append(post)

        offset += count

    return posts

def get_group_subscribers(owner_id, access_token):
    vk_session = vk_api.VkApi(token=access_token)
    vk = vk_session.get_api()

    subscribers = []
    offset = 0
    count = 1000

    while True:
        try:
            response = vk.groups.getMembers(group_id=owner_id, offset=offset, count=count)
            if not response['items']:
                break

            user_ids = response['items']
            users_info = vk.users.get(user_ids=user_ids, fields='city')

            for user in users_info:
                city = user.get('city', {}).get('title', 'Не указан')
                subscribers.append({
                    'id': user['id'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'city': city
                })

            offset += count

        except vk_api.exceptions.VkApiError as e:
            print(f"Ошибка: {e}")
            break

    return subscribers