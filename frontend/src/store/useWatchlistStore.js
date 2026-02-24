import { create } from "zustand";
import { persist } from "zustand/middleware";

const useWatchlistStore = create(
  persist(
    (set) => ({
      watchlist: [],

      // Add a stock to the watchlist
      addStock: (stock) =>
        set((state) => {
          // Prevent duplicates
          const exists = state.watchlist.some(
            (item) => item.ticker === stock.ticker,
          );
          if (exists) return state;
          return { watchlist: [...state.watchlist, stock] };
        }),

      // Remove a stock from the watchlist
      removeStock: (ticker) =>
        set((state) => ({
          watchlist: state.watchlist.filter((item) => item.ticker !== ticker),
        })),

      // Toggle a stock (add if not exists, remove if exists)
      toggleStock: (stock) =>
        set((state) => {
          const exists = state.watchlist.some(
            (item) => item.ticker === stock.ticker,
          );
          if (exists) {
            return {
              watchlist: state.watchlist.filter(
                (item) => item.ticker !== stock.ticker,
              ),
            };
          } else {
            return { watchlist: [...state.watchlist, stock] };
          }
        }),

      // 즐겨찾기 가격 일괄 업데이트
      updatePrices: (priceMap) =>
        set((state) => ({
          watchlist: state.watchlist.map((item) =>
            priceMap[item.ticker] !== undefined
              ? { ...item, price: priceMap[item.ticker] }
              : item,
          ),
        })),

      // Check if a stock is in the watchlist
      isInWatchlist: (ticker) => {
        // This is a helper, but since we can't access get() inside the hook return easily without
        // selecting state, we usually do this in the component:
        // const watchlist = useWatchlistStore(state => state.watchlist);
        // const isSaved = watchlist.some(...)
        // So we might not need a specific action for this, but could be useful if we use getState().
      },
    }),
    {
      name: "watchlist-storage", // unique name for localStorage key
    },
  ),
);

export default useWatchlistStore;
