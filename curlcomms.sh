# c5dfe13b-1508-4fd4-9e08-c90f8b244537  btrinh's FOAF post
# 213f6df00cbe41bbb0e888a62d5780ae btrinh
# d8634b9e2e304323ab18ad16eae7a9fe mrX
STR=$'########################################################\n'
N=$'\n'
echo " #### Get A Post ID: 695fe189-b783-4b74-b679-5b312881909b ###"
echo "$N"
echo "Response: "
echo "$N"
curl -u Nuisance:thought-bubble.herokuapp.com:a --request GET 'http://thought-bubble.herokuapp.com/main/api/getapost/?postid=695fe189-b783-4b74-b679-5b312881909b'
echo "$STR"
echo " #### Get all public posts ###"
curl -u Nuisance:thought-bubble.herokuapp.com:a --request GET 'http://thought-bubble.herokuapp.com/main/api/getposts/'
echo "$STR"
echo " #### Get specific author posts for authenticated user ###"
echo "$N"
echo "Response: "
echo "$N"
curl -u btrinh:thought-bubble.herokuapp.com:a --request GET 'http://thought-bubble.herokuapp.com/main/api/getpostsbyauthor/?authorid=42567a5b-81b8-4962-a9d7-2b558b9da5c9'
echo "$STR"
echo " #### Get posts for currently authenticated user ###"
echo "$N"
echo "Response: "
echo "$N"
curl -u Nuisance:thought-bubble.herokuapp.com:a --request GET 'http://thought-bubble.herokuapp.com/main/api/author/posts2/'
echo "$STR"
echo " #### Get post if FOAF ###"
echo "$N"
echo "Response: "
curl -u Nuisance:thought-bubble.herokuapp.com:a 'http://thought-bubble.herokuapp.com/main/api/Foafvis/'  -X POST  -H "Content-Type: application/json"  -H "Accept: */*"  -d '{"query":"getpost","id":"591bb0b1-e212-4e1c-8ab5-5aa7e513ad1c",
 "author":{
    "id":"4955530c-3267-40e1-8fcc-7fa8cd256c98",
    "host":"http://thought-bubble.herokuapp.com/",
    "displayname":"Nicky Nuisance"
 },
 "friends":[
    "372e86b0-f0f5-4311-9b0f-d1b6fd042462",
    "9f98849f-d827-4c00-ae2d-5cfe2f9ebb09"
 ]
}'
echo "$STR"
echo " ###### Post new friend request (200 OK) #####"
echo "$N"
echo "Response: "
echo "$N"
curl http://thought-bubble.herokuapp.com/main/api/newfriendrequest/  -X POST  -H "Content-Type: application/json"  -H "Accept: */*"  -d '{"query":"friendrequest",
    "author":{
    "id":"6125530c-3267-6ae1-8fcc-7fa8cd256c92",
    "host":"http://thought-bubble.herokuapp.com/",
    "displayname":"RandomNewDude"
    },
    "friend": {
                 "id":"d87e6112-8bb7-470b-986d-6b0c6f9d62f4",
                 "host":"http://thought-bubble.herokuapp.com/",
                 "displayname":"Hnirt",
                 "url":"http://thought-bubble.herokuapp.com/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e"
           }
    }'
echo "$N"
echo "$STR"
echo " ####### Post new friend request (approval pending) #######"
echo "$N"
echo "Response: "
echo "$N"
curl http://thought-bubble.herokuapp.com/main/api/newfriendrequest/  -X POST  -H "Content-Type: application/json"  -H "Accept: */*"  -d '{"query":"friendrequest",
    "author":{
    "id":"4955530c-3267-40e1-8fcc-7fa8cd256c98",
    "host":"http://thought-bubble.herokuapp.com/",
    "displayname":"Nuisance"
    },
    "friend": {
                 "id":"d87e6112-8bb7-470b-986d-6b0c6f9d62f4",
                 "host":"http://thought-bubble.herokuapp.com/",
                 "displayname":"Hnirt",
                 "url":"http://thought-bubble.herokuapp.com/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e"
           }
    }'
echo "$N"
echo "$STR"
echo " ####### Check if friends #######"
echo "$N"
echo "Response: "
echo "$N"
curl http://thought-bubble.herokuapp.com/main/api/checkfriends/?user=d87e6112-8bb7-470b-986d-6b0c6f9d62f4  -X POST  -H "Content-Type: application/json"  -H "Accept: */*"  -d '{"query":"friends","author":"d87e6112-8bb7-470b-986d-6b0c6f9d62f4",
  "authors":[
  "4955530c-3267-40e1-8fcc-7fa8cd256c98","5586a50b-500f-469c-80a1-1bc38a8a819a","b815b07c-2018-4b2c-bc98-d68603975bac", "b3a4098b5de94dd08d1672726737a27b" ]
}'
echo "$N"
echo "$STR"
