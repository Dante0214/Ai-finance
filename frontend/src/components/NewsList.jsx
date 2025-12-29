import React, { useState } from 'react';
import { ExternalLink, ChevronLeft, ChevronRight } from 'lucide-react';

const NewsList = ({ news }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  const indexOfLastNews = currentPage * itemsPerPage;
  const indexOfFirstNews = indexOfLastNews - itemsPerPage;
  const currentNews = news.slice(indexOfFirstNews, indexOfLastNews);
  const totalPages = Math.ceil(news.length / itemsPerPage);

  const handlePrev = () => {
    setCurrentPage((prev) => Math.max(prev - 1, 1));
  };

  const handleNext = () => {
    setCurrentPage((prev) => Math.min(prev + 1, totalPages));
  };

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 h-full flex flex-col">
      <h3 className="text-xl font-semibold text-gray-800 mb-4 flex justify-between items-center">
        Latest News
        <span className="text-xs font-normal text-gray-400 bg-gray-100 px-2 py-1 rounded-full">
          {news.length} relevant articles
        </span>
      </h3>
      
      <div className="flex-1 flex flex-col gap-3 min-h-[400px]">
        {currentNews.map((item, idx) => (
          <a 
            key={idx}
            href={item.link}
            target="_blank"
            rel="noopener noreferrer"
            className="group block"
          >
            <div className="p-3 rounded-xl border border-gray-100 bg-gray-50/50 hover:bg-white hover:border-blue-200 hover:shadow-sm transition-all flex justify-between items-start gap-3">
              <span className="text-sm font-medium text-gray-700 group-hover:text-blue-700 leading-snug line-clamp-2">
                {item.title}
              </span>
              <ExternalLink size={14} className="text-gray-400 group-hover:text-blue-500 flex-shrink-0 mt-0.5" />
            </div>
          </a>
        ))}
        {currentNews.length === 0 && (
          <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">
            No news available
          </div>
        )}
      </div>

      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-between pt-4 border-t border-gray-50">
          <button
            onClick={handlePrev}
            disabled={currentPage === 1}
            className={`p-2 rounded-lg transition-colors ${
              currentPage === 1 
                ? 'text-gray-300 cursor-not-allowed' 
                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
            }`}
          >
            <ChevronLeft size={20} />
          </button>
          
          <span className="text-sm font-medium text-gray-600">
            {currentPage} / {totalPages}
          </span>

          <button
            onClick={handleNext}
            disabled={currentPage === totalPages}
            className={`p-2 rounded-lg transition-colors ${
              currentPage === totalPages 
                ? 'text-gray-300 cursor-not-allowed' 
                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
            }`}
          >
            <ChevronRight size={20} />
          </button>
        </div>
      )}
    </div>
  );
};

export default NewsList;
