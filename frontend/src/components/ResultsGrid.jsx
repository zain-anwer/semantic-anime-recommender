const ResultsGrid = ({ results, loading }) => {

    if (loading) return <p className="text-center text-gray-400 mt-8">Searching...</p>
    if (!results || results.length === 0) return null

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            {results.map((anime) => (
                <div key={anime.mal_id} className="flex gap-3 bg-white/5 border border-white/10 rounded-2xl p-4">
                    <img
                        src={anime.image_url}
                        alt={anime.title}
                        className="w-20 h-28 object-cover rounded-lg flex-shrink-0"
                    />
                    <div className="flex flex-col gap-1 overflow-hidden">
                        <h3 className="font-semibold text-white truncate">{anime.title}</h3>
                        <div className="flex gap-2 text-xs text-gray-400">
                            <span>⭐ {anime.score}</span>
                            <span>· {anime.episodes} eps</span>
                        </div>
                        <div className="flex flex-wrap gap-1 mt-1">
                            {anime.genres.map(g => (
                                <span key={g} className="px-2 py-0.5 bg-purple-500/20 border border-purple-500/30 text-purple-300 text-xs rounded-full">
                                    {g}
                                </span>
                            ))}
                        </div>
                        <p className="text-xs text-gray-500 mt-1 line-clamp-2">{anime.synopsis}</p>
                    </div>
                </div>
            ))}
        </div>
    )
}

export default ResultsGrid