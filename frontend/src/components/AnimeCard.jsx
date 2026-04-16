/*
    1. toFixed(numDecimalPlaces) --> rounds off to the nearest decimal place and returns a string
    2. nullish
*/

const AnimeCard = ({anime}) => {
    return(
        <div className="bg-gray-900 rounded-xl overflow-hidden border border-gray-800 hover:border-purple-500 transition-colors">
            <img 
                src={anime.image_url}
                alt={anime.title}
            />
            <div>
                <h3></h3>
                <p>Score: {anime.score?.toFixed(0) ?? 'N/A'}</p>
                <p>Similarity: {(anime.similarity*100).toFixed(0)}</p>
                <p>
                    Genres: {anime.genres.map(g => <span key={g}>{g}</span>)}
                </p>
            </div>
        </div>
    )
}

export default AnimeCard