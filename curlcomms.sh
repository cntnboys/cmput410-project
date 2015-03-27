# c5dfe13b-1508-4fd4-9e08-c90f8b244537  btrinh's FOAF post
# 213f6df00cbe41bbb0e888a62d5780ae btrinh
# d8634b9e2e304323ab18ad16eae7a9fe mrX
STR=$'########################################################\n'
N=$'\n'
echo " #### Get A Post ID: 37c1792353234b90abe6f4c9e316fab8 ###"
echo "$N"
echo "Response: "
echo "$N"
curl -u admin:host:admin --request GET 'http://thought-bubble.herokuapp.com/main/getapost/?postid=37c1792353234b90abe6f4c9e316fab8'
echo "$STR"
echo " #### Get all public posts ###"
curl -u btrinh:127.0.0.1:a --request GET 'http://thought-bubble.herokuapp.com/main/getposts/'
echo "$STR"
echo " #### Get specific author posts for authenticated user ###"
echo "$N"
echo "Response: "
echo "$N"
curl -u admin:host:admin --request GET 'http://thought-bubble.herokuapp.com/main/getauthorposts/?authorid=d8634b9e2e304323ab18ad16eae7a9fe' 
echo "$STR"
echo " #### Get posts for currently authenticated user ###"
echo "$N"
echo "Response: "
echo "$N"
curl -u admin:host:admin --request GET 'thought-bubble.herokuapp.com/main/author/posts2/'
echo "$STR"
echo " #### Get post if FOAF ###"
echo "$N"
echo "Response: "
curl -u admin:host:admin http://thought-bubble.herokuapp.com/main/Foafvis/  -X POST  -H "Content-Type: application/json"  -H "Accept: */*"  -d '{"query":"getpost","id":"c5dfe13b15084fd49e08c90f8b244537",
 "author":{
    "id":"d8634b9e2e304323ab18ad16eae7a9fe",
    "host":"http://thought-bubble.herokuapp.com/",
    "displayname":"mrX"
 },
 "friends":[
    "073da573c0794ddb85cfd9800dd56196",
    "40e454acecf84e7684771031c3c78751"
 ]
}'
echo "$STR"
echo " ###### Post new friend request #####"
echo "$N"
echo "Response: "
echo "$N"
curl http://thought-bubble.herokuapp.com/main/newfriendrequest/  -X POST  -H "Content-Type: application/json"  -H "Accept: */*"  -d '{"query":"friendrequest",
    "author":{
    "id":"d8634b9e2e304323ab18ad16eae7a9fe ",
    "host":"http://thought-bubble.herokuapp.com/",
    "displayname":"mrX"
    },
    "friend": {
                 "id":"213f6df00cbe41bbb0e888a62d5780ae",
                 "host":"http://thought-bubble.herokuapp.com/",
                 "displayname":"llkay",
                 "url":"http://thought-bubble.herokuapp.com/author/9de17f29c12e8f97bcbbd34cc908f1baba40658e"
           }
    }'

echo "$STR"
echo " ####### Check if friends #######"
echo "$N"
echo "Response: "
echo "$N"
curl http://thought-bubble.herokuapp.com/main/checkfriends/?user=213f6df00cbe41bbb0e888a62d5780ae  -X POST  -H "Content-Type: application/json"  -H "Accept: */*"  -d '{"query":"friends","author":"213f6df00cbe41bbb0e888a62d5780ae",
  "authors":[
  "40e454acecf84e7684771031c3c78751","5234a3e9c05a42a8b45735ec80cc679a","073da573c0794ddb85cfd9800dd56196", "b3a4098b5de94dd08d1672726737a27b" ]
}'
echo "$STR"
