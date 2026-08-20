import { Link } from 'react-router-dom';
import { Home } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1B4332] via-[#2D6A4F] to-[#40916C] flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-9xl font-bold text-white mb-4">404</h1>
        <h2 className="text-3xl font-bold text-white mb-4">Page Not Found</h2>
        <p className="text-white/80 mb-8 max-w-md mx-auto">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link
          to="/home"
          className="inline-flex items-center px-6 py-3 bg-white text-[#1B4332] rounded-lg font-semibold hover:bg-gray-100 transition-all transform hover:scale-105 shadow-lg"
        >
          <Home size={20} className="mr-2" />
          Back to Home
        </Link>
      </div>
    </div>
  );
}
