import {useState,useCallback} from 'react'
import getRecommendations from '../api/recommend'

const useRecommendations = () => {
        
    const [loading,setLoading] = useState(false)
    const [error,setError] = useState(false)
    const [mode,setMode] = useState(null)
    const [results,setResults] = useState([])

    const search = useCallback(async(query,filters) => {
            
        // if query is empty

        if (!query.trim())
            return

        try {
            setLoading(true)
            const data = await getRecommendations(query,filters)
            setMode(data.response_type)
            setResults(data.anime_list)
        }
        catch (error) {
            setError(error.message)
            throw error
        }
        finally {
            setLoading(false)
        }
    },[])

    return {mode, results, loading, error, search}
}

export default useRecommendations
