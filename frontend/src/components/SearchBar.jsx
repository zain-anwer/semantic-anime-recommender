import {useState} from 'react'

const SearchBar = ({onSearch,loading}) =>{

    const [query,setQuery] = useState('')
    const [score,setScore] = useState(0)
    const [selectedGenres,setSelectedGenres] = useState([])

    const genres = ['Action', 'Award Winning', 'Sci-Fi', 'Adventure', 
                        'Drama', 'Mystery', 'Supernatural', 'Fantasy', 
                        'Sports', 'Comedy', 'Romance', 'Suspense', 'Ecchi', 
                        'Avant Garde', 'Gourmet', 'Horror', 'Slice of Life']

    const toggleGenre = (genre) => 
    {
        setSelectedGenres(
            prev => prev.includes(genre)? prev.filter(g => g !== genre) : [...prev,genre] 
        )
    }

    const submitHandler = (e) =>
    {
        e.preventDefault()
        onSearch(query,{score,'genres':selectedGenres})
    }

    return(
        <form onSubmit={submitHandler} className="flex flex-col gap-2">
            <div className="flex gap-2">
                <input
                    type="text"
                    placeholder="e.g. Something dark and psychological"
                    value={query}
                    onChange={(e) => {setQuery(e.target.value)}}
                    className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                />
                <button 
                    className="bg-purple-600 hover:bg-purple-700 disabled:opacity-70 px-6 py-3 rounded-lg font-medium transition-colors"
                    type="submit" disabled={loading || !query.trim()}>
                        {loading ? "searching..." : "search"}
                </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 p-4 bg-white/[0.02] border border-white/5 rounded-2xl">
                
                {/* score slider */}
              
                <div className="flex flex-col gap-3">
                    <div className="flex justify-between text-xs font-bold tracking-widest text-gray-400 uppercase">
                        <span>Min Score</span>
                        <span className="text-purple-400">{score > 0 ? score : 'Any'}</span>
                    </div>
                    <input 
                        type="range" min="0" max="10" step="0.05"
                        value={score}
                        onChange={(e) => setScore(e.target.value)}
                        className="w-full h-1.5 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
                    />
                </div>

                {/* genre tags */}

                <div className="flex flex-col gap-3">
                    <span className="text-xs font-bold tracking-widest text-gray-400 uppercase">Genres</span>
                    <div className="flex flex-wrap gap-2 max-h-20 overflow-y-auto custom-scrollbar">
                        {genres.map(genre => (
                            <button
                                type="button"
                                key={genre}
                                onClick={() => toggleGenre(genre)}
                                className={`px-3 py-1 rounded-full text-xs font-medium transition-all border ${
                                    selectedGenres.includes(genre) 
                                    ? 'bg-white-500/20 border-purple-500 text-purple-200' 
                                    : 'bg-white/5 border-white/10 text-gray-400 hover:border-white/20'
                                }`}
                            >
                                {genre}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </form>
    )

}

export default SearchBar