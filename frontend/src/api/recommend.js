import axios from 'axios'

const BASE_URL = import.meta.env.VITE_BACKEND_URL

const getRecommendations = async(query,filters) => {
    try {
        const res = await axios.post(`${BASE_URL}/recommend-anime`,
        {
            'query' : query,
            'limit' : filters.limit || 10,
            'min_score' : filters.score || null,
            'genres':filters.genres || null,
        })
        // return data
        return res.data
    }
    catch(error) {
        // we will be sending a message in case of error from the backend
        console.log("Error in recommendation api: ",error.message)
    }
} 

export default getRecommendations