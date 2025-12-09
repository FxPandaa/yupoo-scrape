'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, Filter, X, ExternalLink, ShoppingCart, Tag, Store, ChevronLeft, ChevronRight, Loader2, Package, RefreshCw } from 'lucide-react';

const API_BASE = '/api';

export default function Home() {
  // State
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Search & filters
  const [query, setQuery] = useState('');
  const [selectedSeller, setSelectedSeller] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  
  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const perPage = 48;
  
  // Facets
  const [sellers, setSellers] = useState([]);
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  
  // UI state
  const [showFilters, setShowFilters] = useState(false);
  const [stats, setStats] = useState(null);
  const [scrapeStatus, setScrapeStatus] = useState(null);

  // Fetch products
  const fetchProducts = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      if (query) params.set('q', query);
      if (selectedSeller) params.set('seller', selectedSeller);
      if (selectedCategory) params.set('category', selectedCategory);
      if (selectedBrand) params.set('brand', selectedBrand);
      if (minPrice) params.set('min_price', minPrice);
      if (maxPrice) params.set('max_price', maxPrice);
      params.set('page', page.toString());
      params.set('per_page', perPage.toString());
      
      const response = await fetch(`${API_BASE}/search?${params}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      
      setProducts(data.products || []);
      setTotal(data.total || 0);
      setTotalPages(data.total_pages || 1);
      
      // Update facets
      if (data.facets) {
        if (data.facets.seller) setSellers(data.facets.seller);
        if (data.facets.category) setCategories(data.facets.category);
        if (data.facets.brand) setBrands(data.facets.brand);
      }
      
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to load products. Please try again.');
      setProducts([]);
    } finally {
      setLoading(false);
    }
  }, [query, selectedSeller, selectedCategory, selectedBrand, minPrice, maxPrice, page]);

  // Fetch stats
  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/stats`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Stats error:', err);
    }
  };

  // Fetch scrape status
  const fetchScrapeStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/scrape/status`);
      if (response.ok) {
        const data = await response.json();
        setScrapeStatus(data);
      }
    } catch (err) {
      console.error('Scrape status error:', err);
    }
  };

  // Start scraping
  const startScraping = async () => {
    try {
      const response = await fetch(`${API_BASE}/scrape/start`, {
        method: 'POST',
      });
      if (response.ok) {
        fetchScrapeStatus();
      }
    } catch (err) {
      console.error('Start scrape error:', err);
    }
  };

  // Initial load
  useEffect(() => {
    fetchProducts();
    fetchStats();
    fetchScrapeStatus();
  }, [fetchProducts]);

  // Poll scrape status while running
  useEffect(() => {
    if (scrapeStatus?.is_running) {
      const interval = setInterval(fetchScrapeStatus, 2000);
      return () => clearInterval(interval);
    }
  }, [scrapeStatus?.is_running]);

  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchProducts();
  };

  // Clear filters
  const clearFilters = () => {
    setQuery('');
    setSelectedSeller('');
    setSelectedCategory('');
    setSelectedBrand('');
    setMinPrice('');
    setMaxPrice('');
    setPage(1);
  };

  // Format price
  const formatPrice = (price, currency = 'CNY') => {
    if (!price) return null;
    return `¥${price.toFixed(0)}`;
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      {/* Header */}
      <header className="bg-[#111] border-b border-gray-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between gap-4">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <Package className="w-8 h-8 text-orange-500" />
              <div>
                <h1 className="text-xl font-bold text-white">Yupoo Search</h1>
                <p className="text-xs text-gray-500">
                  {stats ? `${stats.total_products.toLocaleString()} products from ${stats.total_sellers} sellers` : 'Loading...'}
                </p>
              </div>
            </div>
            
            {/* Search bar */}
            <form onSubmit={handleSearch} className="flex-1 max-w-2xl">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search products, brands, sellers..."
                  className="w-full pl-12 pr-4 py-3 bg-[#1a1a1a] border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500"
                />
              </div>
            </form>
            
            {/* Actions */}
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${
                  showFilters ? 'bg-orange-500 border-orange-500 text-white' : 'border-gray-700 text-gray-300 hover:border-gray-600'
                }`}
              >
                <Filter className="w-4 h-4" />
                Filters
              </button>
              
              <button
                onClick={startScraping}
                disabled={scrapeStatus?.is_running}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg text-white"
              >
                <RefreshCw className={`w-4 h-4 ${scrapeStatus?.is_running ? 'animate-spin' : ''}`} />
                {scrapeStatus?.is_running ? 'Scraping...' : 'Scrape All'}
              </button>
            </div>
          </div>
          
          {/* Scraping progress */}
          {scrapeStatus?.is_running && (
            <div className="mt-4 bg-[#1a1a1a] rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">
                  Scraping: <span className="text-white">{scrapeStatus.current_seller}</span>
                </span>
                <span className="text-sm text-gray-400">
                  {scrapeStatus.progress} / {scrapeStatus.total_sellers} sellers
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-orange-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(scrapeStatus.progress / scrapeStatus.total_sellers) * 100}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-2">
                {scrapeStatus.products_found.toLocaleString()} products found
              </p>
            </div>
          )}
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex gap-6">
          {/* Filters sidebar */}
          {showFilters && (
            <aside className="w-64 flex-shrink-0">
              <div className="bg-[#111] rounded-xl border border-gray-800 p-4 sticky top-24">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-semibold text-white">Filters</h2>
                  <button onClick={clearFilters} className="text-sm text-orange-500 hover:text-orange-400">
                    Clear all
                  </button>
                </div>
                
                {/* Seller filter */}
                <div className="filter-section">
                  <label className="block text-sm font-medium text-gray-400 mb-2">Seller</label>
                  <select
                    value={selectedSeller}
                    onChange={(e) => { setSelectedSeller(e.target.value); setPage(1); }}
                    className="w-full bg-[#1a1a1a] border border-gray-700 rounded-lg px-3 py-2 text-white text-sm"
                  >
                    <option value="">All sellers</option>
                    {sellers.map((s) => (
                      <option key={s.value} value={s.value}>
                        {s.value} ({s.count})
                      </option>
                    ))}
                  </select>
                </div>
                
                {/* Category filter */}
                <div className="filter-section">
                  <label className="block text-sm font-medium text-gray-400 mb-2">Category</label>
                  <select
                    value={selectedCategory}
                    onChange={(e) => { setSelectedCategory(e.target.value); setPage(1); }}
                    className="w-full bg-[#1a1a1a] border border-gray-700 rounded-lg px-3 py-2 text-white text-sm"
                  >
                    <option value="">All categories</option>
                    {categories.map((c) => (
                      <option key={c.value} value={c.value}>
                        {c.value}
                      </option>
                    ))}
                  </select>
                </div>
                
                {/* Brand filter */}
                <div className="filter-section">
                  <label className="block text-sm font-medium text-gray-400 mb-2">Brand</label>
                  <select
                    value={selectedBrand}
                    onChange={(e) => { setSelectedBrand(e.target.value); setPage(1); }}
                    className="w-full bg-[#1a1a1a] border border-gray-700 rounded-lg px-3 py-2 text-white text-sm"
                  >
                    <option value="">All brands</option>
                    {brands.map((b) => (
                      <option key={b.value} value={b.value}>
                        {b.value}
                      </option>
                    ))}
                  </select>
                </div>
                
                {/* Price filter */}
                <div className="filter-section">
                  <label className="block text-sm font-medium text-gray-400 mb-2">Price (¥)</label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      value={minPrice}
                      onChange={(e) => setMinPrice(e.target.value)}
                      placeholder="Min"
                      className="w-1/2 bg-[#1a1a1a] border border-gray-700 rounded-lg px-3 py-2 text-white text-sm"
                    />
                    <input
                      type="number"
                      value={maxPrice}
                      onChange={(e) => setMaxPrice(e.target.value)}
                      placeholder="Max"
                      className="w-1/2 bg-[#1a1a1a] border border-gray-700 rounded-lg px-3 py-2 text-white text-sm"
                    />
                  </div>
                </div>
                
                <button
                  onClick={() => { setPage(1); fetchProducts(); }}
                  className="w-full bg-orange-500 hover:bg-orange-400 text-white py-2 rounded-lg font-medium"
                >
                  Apply Filters
                </button>
              </div>
            </aside>
          )}

          {/* Main content */}
          <main className="flex-1">
            {/* Results info */}
            <div className="flex items-center justify-between mb-4">
              <p className="text-gray-400">
                {loading ? 'Searching...' : `${total.toLocaleString()} products found`}
              </p>
              
              {/* Active filters */}
              <div className="flex gap-2">
                {selectedSeller && (
                  <span className="badge badge-brand flex items-center gap-1">
                    <Store className="w-3 h-3" />
                    {selectedSeller}
                    <button onClick={() => setSelectedSeller('')}><X className="w-3 h-3" /></button>
                  </span>
                )}
                {selectedCategory && (
                  <span className="badge badge-category flex items-center gap-1">
                    {selectedCategory}
                    <button onClick={() => setSelectedCategory('')}><X className="w-3 h-3" /></button>
                  </span>
                )}
                {selectedBrand && (
                  <span className="badge badge-brand flex items-center gap-1">
                    <Tag className="w-3 h-3" />
                    {selectedBrand}
                    <button onClick={() => setSelectedBrand('')}><X className="w-3 h-3" /></button>
                  </span>
                )}
              </div>
            </div>

            {/* Loading state */}
            {loading && (
              <div className="flex items-center justify-center py-20">
                <Loader2 className="w-8 h-8 text-orange-500 animate-spin" />
              </div>
            )}

            {/* Error state */}
            {error && (
              <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-6 text-center">
                <p className="text-red-400">{error}</p>
                <button
                  onClick={fetchProducts}
                  className="mt-4 px-4 py-2 bg-red-500 hover:bg-red-400 text-white rounded-lg"
                >
                  Retry
                </button>
              </div>
            )}

            {/* Empty state */}
            {!loading && !error && products.length === 0 && (
              <div className="text-center py-20">
                <Package className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">No products found</h3>
                <p className="text-gray-500 mb-4">Try adjusting your search or filters</p>
                <button
                  onClick={clearFilters}
                  className="px-4 py-2 bg-orange-500 hover:bg-orange-400 text-white rounded-lg"
                >
                  Clear all filters
                </button>
              </div>
            )}

            {/* Products grid */}
            {!loading && !error && products.length > 0 && (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {products.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            )}

            {/* Pagination */}
            {!loading && totalPages > 1 && (
              <div className="flex items-center justify-center gap-4 mt-8">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="flex items-center gap-2 px-4 py-2 bg-[#1a1a1a] border border-gray-700 rounded-lg text-white disabled:opacity-50 disabled:cursor-not-allowed hover:border-gray-600"
                >
                  <ChevronLeft className="w-4 h-4" />
                  Previous
                </button>
                
                <span className="text-gray-400">
                  Page {page} of {totalPages}
                </span>
                
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="flex items-center gap-2 px-4 py-2 bg-[#1a1a1a] border border-gray-700 rounded-lg text-white disabled:opacity-50 disabled:cursor-not-allowed hover:border-gray-600"
                >
                  Next
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}

// Product card component
function ProductCard({ product }) {
  const [imageError, setImageError] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  const formatPrice = (price) => {
    if (!price) return null;
    return `¥${price.toFixed(0)}`;
  };

  return (
    <div className="product-card bg-[#111] border border-gray-800 rounded-xl overflow-hidden group">
      {/* Image */}
      <div className="relative aspect-square bg-[#1a1a1a]">
        {!imageLoaded && !imageError && (
          <div className="absolute inset-0 image-skeleton" />
        )}
        
        {product.image_url && !imageError ? (
          <img
            src={product.image_url}
            alt={product.title}
            className={`w-full h-full object-cover transition-opacity duration-300 ${imageLoaded ? 'opacity-100' : 'opacity-0'}`}
            onLoad={() => setImageLoaded(true)}
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Package className="w-12 h-12 text-gray-700" />
          </div>
        )}
        
        {/* Price badge */}
        {product.price && (
          <div className="absolute top-2 right-2 badge badge-price">
            {formatPrice(product.price)}
          </div>
        )}
        
        {/* Weidian indicator */}
        {product.weidian_url && (
          <div className="absolute top-2 left-2 badge badge-weidian">
            Weidian
          </div>
        )}
        
        {/* Hover overlay */}
        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <a
            href={product.url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-3 bg-white/20 hover:bg-white/30 rounded-full"
            title="View on Yupoo"
          >
            <ExternalLink className="w-5 h-5 text-white" />
          </a>
          
          {product.weidian_url && (
            <a
              href={product.weidian_url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-3 bg-orange-500 hover:bg-orange-400 rounded-full"
              title="Buy on Weidian"
            >
              <ShoppingCart className="w-5 h-5 text-white" />
            </a>
          )}
        </div>
      </div>
      
      {/* Info */}
      <div className="p-3">
        <h3 className="text-sm text-white font-medium line-clamp-2 mb-2" title={product.title}>
          {product.title}
        </h3>
        
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500">{product.seller}</span>
          
          {product.brand && (
            <span className="text-xs text-blue-400">{product.brand}</span>
          )}
        </div>
        
        {product.category && (
          <span className="inline-block mt-2 text-xs text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded">
            {product.category}
          </span>
        )}
      </div>
    </div>
  );
}
