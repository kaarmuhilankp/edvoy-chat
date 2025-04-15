import streamlit as st
import requests
import random

def query_edvoy_courses(course_payload):
    """ Query Edvoy GraphQL API for courses based on the generated search term and filters """
    url = "https://api-dev.edvoy.com/edp/graphql"
    
    # Corrected headers from your provided script
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Connection": "keep-alive",
        "DNT": "1",
        "Origin": "https://api-dev.edvoy.com"
    }

    # Extract filters from the course payload
    filters = course_payload.get("filter", {})
    paging = course_payload.get("paging", {"limit": 10, "offset": 0})
    query = course_payload.get("query", "")
    search_type = course_payload.get("searchType", "SmartSearch")
    filter_type = course_payload.get("filterType", "crm")

    # Construct the GraphQL query dynamically
    graphql_query = """
    query courseESSearchv2(
      $filter: CourseFilterInputDto!, 
      $filterType: String = "crm", 
      $paging: PagingInputDto = {limit: 10, offset: 0},
      $query: String = "", 
      $searchType: CourseSearchTypeEnum = SmartSearch
    ) {
      searchCourse(
        filter: $filter
        paging: $paging
        query: $query
        filterType: $filterType
        searchType: $searchType
      ) {
        count
        items {
          _id
          name
          globalScore
          courseDuration
          currency
          institution {
            name
            address {
              country
              city
            }
          }
          approxAnnualFee
        }
      }
    }
    """
    
    variables = {
        "filter": filters,
        "paging": paging,
        "query": query,
        "searchType": search_type,
        "filterType": filter_type
    }

    # Prepare the request payload
    payload = {
        "query": graphql_query,
        "variables": variables
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return {"status": "error", "message": f"API request failed: {str(e)}", "data": None}

# Generate a unique username for each session
if 'username' not in st.session_state:
    st.session_state['username'] = f"student{random.randint(10000, 99999)}"

# Initialize the conversation history in session state
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []

# Streamlit app title and session username
st.title("Edvoy Chat Bot")
st.write(f"Your session username: **{st.session_state['username']}**")

# Input field for user query
query = st.text_input("Ask:", "")

# Display result when user submits a query
if st.button("Send Query"):
    if query.strip():
        try:
            # Prepare the payload for the chatbot query
            payload = {
                "query": query,
                "username": st.session_state['username']
            }
            
            # Call the chatbot API to get a response
            response = requests.post(
                "https://api-qa.edvoy.com/chat-bot/query",
                headers={"Content-Type": "application/json"},
                json=payload
            )

            if response.status_code == 200:
                data = response.json()

                # Display the AI response
                bot_response = data.get("response", "")
                st.subheader("AI Response")
                st.write(bot_response)

                # Parse and handle the response with course data
                course_payload = data.get("course")  # Extract course data from response
                if course_payload:
                    course_data = query_edvoy_courses(course_payload)
                    if course_data and course_data.get("data"):
                        courses = course_data["data"]["searchCourse"]["items"]
                        st.subheader("Courses")
                        for course in courses[:3]:  # Display a few courses
                            st.write(f"**Course Name:** {course['name']}")
                            st.write(f"**Annual Fee:** {course['currency']}{course['approxAnnualFee']}")
                            st.write(f"**Institution:** {course['institution']['name']}")

                            st.write("---")  # Divider for clarity

                # Display the raw chatbot API response in an expandable section
                with st.expander("View Raw Chatbot API Response"):
                    st.json(data)  # Display the entire response from the chatbot API

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a query.")
