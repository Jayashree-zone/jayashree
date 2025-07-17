import React, { useState, useEffect } from 'react';
import { postsApi } from './api';
import type { Post } from './api';

const PostList: React.FC = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrev, setHasPrev] = useState(false);
  const [total, setTotal] = useState(0);

  // Load posts
  const loadPosts = async (pageNum: number = 1) => {
    try {
      setLoading(true);
      setError('');
      
      const response = await postsApi.getPosts(pageNum, 10);
      setPosts(response.posts);
      setPage(response.pagination.page);
      setHasNext(response.pagination.has_next);
      setHasPrev(response.pagination.has_prev);
      setTotal(response.pagination.total);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to load posts');
    } finally {
      setLoading(false);
    }
  };

  // Handle like/unlike
  const handleLike = async (postId: number) => {
    try {
      const result = await postsApi.likePost(postId);
      
      // Update the post in the list
      setPosts(prevPosts => 
        prevPosts.map(post => 
          post.id === postId 
            ? { ...post, likes_count: result.likes_count, is_liked: result.is_liked }
            : post
        )
      );
    } catch (error) {
      console.error('Failed to like post:', error);
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
      const diffInMinutes = Math.floor(diffInHours * 60);
      return `${diffInMinutes}m ago`;
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays}d ago`;
    }
  };

  // Load posts on component mount
  useEffect(() => {
    loadPosts();
  }, []);

  // Handle pagination
  const handleNextPage = () => {
    if (hasNext) {
      loadPosts(page + 1);
    }
  };

  const handlePrevPage = () => {
    if (hasPrev) {
      loadPosts(page - 1);
    }
  };

  if (loading && posts.length === 0) {
    return (
      <div className="max-w-2xl mx-auto p-4">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-center py-8">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            <span className="ml-3 text-gray-600">Loading posts...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error && posts.length === 0) {
    return (
      <div className="max-w-2xl mx-auto p-4">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-center py-8">
            <div className="text-red-600 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Posts</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={() => loadPosts()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (posts.length === 0) {
    return (
      <div className="max-w-2xl mx-auto p-4">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-center py-8">
            <div className="text-gray-400 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Posts Yet</h3>
            <p className="text-gray-600">Be the first to share something!</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-4">
      {/* Posts */}
      {posts.map((post) => (
        <div key={post.id} className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Post Header */}
          <div className="p-4 border-b border-gray-100">
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                {post.user.avatar_url ? (
                  <img
                    src={post.user.avatar_url}
                    alt={post.user.username}
                    className="w-10 h-10 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                    <span className="text-gray-600 font-medium text-sm">
                      {post.user.username.charAt(0).toUpperCase()}
                    </span>
                  </div>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">
                  {post.user.username}
                </p>
                <p className="text-sm text-gray-500">
                  {formatDate(post.created_at)}
                </p>
              </div>
            </div>
          </div>

          {/* Post Content */}
          <div className="p-4">
            <div className="text-gray-800 whitespace-pre-wrap mb-4">
              {post.content}
            </div>

            {/* Post Media */}
            {post.media_url && (
              <div className="mb-4">
                {post.media_type === 'image' ? (
                  <img
                    src={post.media_url}
                    alt="Post media"
                    className="w-full rounded-lg object-cover max-h-96"
                  />
                ) : post.media_type === 'video' ? (
                  <video
                    src={post.media_url}
                    controls
                    className="w-full rounded-lg max-h-96"
                  />
                ) : null}
              </div>
            )}

            {/* Post Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-100">
              <button
                onClick={() => handleLike(post.id)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors duration-200 ${
                  post.is_liked
                    ? 'text-red-600 bg-red-50 hover:bg-red-100'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <svg
                  className={`w-5 h-5 ${post.is_liked ? 'fill-current' : 'stroke-current fill-none'}`}
                  viewBox="0 0 24 24"
                  strokeWidth={post.is_liked ? 0 : 2}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
                <span className="text-sm font-medium">
                  {post.likes_count} {post.likes_count === 1 ? 'like' : 'likes'}
                </span>
              </button>

              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <button className="flex items-center space-x-1 hover:text-gray-700 transition-colors duration-200">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <span>Comment</span>
                </button>
                <button className="flex items-center space-x-1 hover:text-gray-700 transition-colors duration-200">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                  </svg>
                  <span>Share</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      ))}

      {/* Pagination */}
      {(hasNext || hasPrev) && (
        <div className="bg-white rounded-lg shadow-lg p-4">
          <div className="flex items-center justify-between">
            <button
              onClick={handlePrevPage}
              disabled={!hasPrev || loading}
              className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
                !hasPrev || loading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              Previous
            </button>

            <span className="text-sm text-gray-600">
              Page {page} of {Math.ceil(total / 10)}
            </span>

            <button
              onClick={handleNextPage}
              disabled={!hasNext || loading}
              className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
                !hasNext || loading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Loading indicator for pagination */}
      {loading && posts.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-4">
          <div className="flex items-center justify-center py-4">
            <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            <span className="ml-3 text-gray-600">Loading more posts...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default PostList; 