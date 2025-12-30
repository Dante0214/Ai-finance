import { Home } from "lucide-react";

function MobileHeader({ onReset, children }) {
  return (
    <div className="md:hidden flex items-center gap-2 pt-6 pb-4">
      {/* 홈 버튼: items-center로 인해 세로 중앙 정렬됨 */}
      <button
        onClick={onReset}
        className="p-2 text-gray-600 hover:bg-gray-100 rounded-full transition-colors flex-shrink-0 flex items-center justify-center"
        aria-label="Home"
      >
        <Home size={24} />
      </button>

      {/* 서치바 영역: flex-1로 남은 공간 차지 */}
      <div className="flex-1 flex items-center">{children}</div>
    </div>
  );
}

export default MobileHeader;
