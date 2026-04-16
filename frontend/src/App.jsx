/*
1. <aside> tag is used to

*/


import { useState } from 'react'
import SearchBar from './components/SearchBar'
import ResultsGrid from './components/ResultsGrid'
import useRecommendations from './hooks/useRecommendations'

const App = () => {
    const { results, loading, error, mode, search } = useRecommendations()
    const leftCharacters = ['/bg_1.png','/bg_2.png','/bg_3.png']
    const rightCharacters = ['/bg_5.png','/bg_6.png','/bg_7.png']

    //"bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl backdrop-saturate-150"

    return (
        <div className="min-h-screen text-white px-6 py-12 flex items-center justify-center relative overflow-hidden">
            
            {/* left character stage */ }
            
            <aside className="hidden xl:flex fixed left-0 top-0 w-[15%] h-full flex-col justify-around items-center p-4 z-0 opacity-80 pointer-events-none">
                {leftCharacters.map((src, i) => (
                    <img 
                        key={i} 
                        src={src} 
                        alt="character" 
                        className="w-full h-[40%] object-contain transition-opacity duration-700 hover:opacity-100" 
                    />
                ))}
            </aside>

            <div className="z-10 
                h-[95vh] w-[80%] md:w-[50vw] 
                bg-white/[0.03] backdrop-blur-2xl backdrop-saturate-150
                border border-white/10 rounded-[3rem]
                shadow-2xl flex flex-col p-8 md:p-12 
                overflow-y-auto custom-scrollbar">
                <h1 className="text-4xl font-bold text-center mb-2">
                    Anime Recommender Engine
                </h1>
                <p className="text-center text-gray-400 mb-8">
                    Describe a vibe or search by anime name
                </p>
                <SearchBar onSearch={search} loading={loading} />
                {mode && (
                    <p className="text-sm text-gray-500 mt-4 text-center">
                        Mode: <span className="text-purple-400">{mode}</span>
                    </p>
                )}
                {error && <p className="text-red-400 text-center mt-4">{error}</p>}
                <ResultsGrid results={results} loading={loading} />
            </div>

            {/* right character stage */}
           
            <aside className="hidden xl:flex fixed right-0 top-0 w-[15%] h-full flex-col justify-around items-center p-4 z-0 opacity-80 pointer-events-none">
                {rightCharacters.map((src, i) => (
                    <img 
                        key={i} 
                        src={src} 
                        alt="character" 
                        className="w-full h-[40%] object-contain" 
                    />
                ))}
            </aside>

        </div>
    )
}

export default App