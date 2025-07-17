import React, { useState, useRef, useCallback } from 'react';
import { postsApi } from './api';
import type { PostData } from './api';

interface MediaFile {
  file: File;
  preview: string;
  type: 'image' | 'video';
}

const PostCreate: React.FC = () => {
  const [content, setContent] = useState('');
  const [mediaFiles, setMediaFiles] = useState<MediaFile[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{ [key: string]: number }>({});
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Character count
  const charCount = content.length;
  const maxChars = 1000;
  const isOverLimit = charCount > maxChars;

  // Handle text input with auto-resize
  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setContent(value);
    
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  // Handle file selection
  const handleFileSelect = (files: FileList | null) => {
    if (!files) return;

    const newMediaFiles: MediaFile[] = [];
    
    Array.from(files).forEach(file => {
      // Validate file type
      const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'video/mp4', 'video/mov', 'video/avi'];
      if (!validTypes.includes(file.type)) {
        setError(`Invalid file type: ${file.name}. Only images (JPG, PNG, GIF) and videos (MP4, MOV, AVI) are allowed.`);
        return;
      }

      // Validate file size (10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError(`File too large: ${file.name}. Maximum size is 10MB.`);
        return;
      }

      const type = file.type.startsWith('image/') ? 'image' : 'video';
      const preview = URL.createObjectURL(file);
      
      newMediaFiles.push({ file, preview, type });
    });

    setMediaFiles(prev => [...prev, ...newMediaFiles]);
    setError('');
  };

  // Handle drag and drop
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.add('border-blue-500', 'bg-blue-50');
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.remove('border-blue-500', 'bg-blue-50');
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.remove('border-blue-500', 'bg-blue-50');
    handleFileSelect(e.dataTransfer.files);
  }, []);

  // Remove media file
  const removeMediaFile = (index: number) => {
    setMediaFiles(prev => {
      const newFiles = [...prev];
      URL.revokeObjectURL(newFiles[index].preview);
      newFiles.splice(index, 1);
      return newFiles;
    });
  };

  // Upload media files
  const uploadMediaFiles = async (): Promise<{ media_url: string; media_type: string }[]> => {
    const uploadPromises = mediaFiles.map(async (mediaFile, index) => {
      try {
        setUploadProgress(prev => ({ ...prev, [index]: 0 }));
        
        const result = await postsApi.uploadMedia(mediaFile.file);
        
        setUploadProgress(prev => ({ ...prev, [index]: 100 }));
        return result;
      } catch (error) {
        throw new Error(`Failed to upload ${mediaFile.file.name}: ${error}`);
      }
    });

    return Promise.all(uploadPromises);
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!content.trim()) {
      setError('Post content is required');
      return;
    }

    if (isOverLimit) {
      setError('Post content is too long');
      return;
    }

    setIsSubmitting(true);
    setError('');
    setSuccess('');

    try {
      let mediaUrl: string | undefined;
      let mediaType: string | undefined;

      // Upload media files if any
      if (mediaFiles.length > 0) {
        const uploadResults = await uploadMediaFiles();
        // For now, we'll use the first media file
        if (uploadResults.length > 0) {
          mediaUrl = uploadResults[0].media_url;
          mediaType = uploadResults[0].media_type;
        }
      }

      // Create post
      const postData: PostData = {
        content: content.trim(),
        media_url: mediaUrl,
        media_type: mediaType
      };

      await postsApi.createPost(postData);

      // Reset form
      setContent('');
      setMediaFiles([]);
      setShowPreview(false);
      setSuccess('Post created successfully!');
      
      // Clear textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }

    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to create post');
    } finally {
      setIsSubmitting(false);
      setUploadProgress({});
    }
  };

  // Format text for preview (simple markdown-like formatting)
  const formatContent = (text: string) => {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">Create Post</h2>
        
        {/* Error/Success Messages */}
        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}
        
        {success && (
          <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Content Textarea */}
          <div>
            <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
              What's on your mind?
            </label>
            <div className="relative">
              <textarea
                ref={textareaRef}
                id="content"
                value={content}
                onChange={handleContentChange}
                placeholder="Share your thoughts, ideas, or experiences..."
                className={`w-full p-4 border rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ${
                  isOverLimit ? 'border-red-500' : 'border-gray-300'
                }`}
                rows={4}
                maxLength={maxChars}
              />
              
              {/* Character count */}
              <div className={`text-sm mt-1 text-right ${
                isOverLimit ? 'text-red-600' : 'text-gray-500'
              }`}>
                {charCount}/{maxChars}
              </div>
            </div>
          </div>

          {/* Media Upload Area */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Add Media (Optional)
            </label>
            
            {/* Drag & Drop Zone */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors duration-200"
            >
              <div className="space-y-2">
                <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <div className="text-gray-600">
                  <span className="font-medium">Click to upload</span> or drag and drop
                </div>
                <p className="text-xs text-gray-500">
                  Images (JPG, PNG, GIF) and Videos (MP4, MOV, AVI) up to 10MB
                </p>
              </div>
              
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*,video/*"
                onChange={(e) => handleFileSelect(e.target.files)}
                className="hidden"
              />
              
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
              >
                Choose Files
              </button>
            </div>
          </div>

          {/* Media Preview */}
          {mediaFiles.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Selected Media:</h3>
              <div className="grid grid-cols-2 gap-4">
                {mediaFiles.map((mediaFile, index) => (
                  <div key={index} className="relative group">
                    <div className="relative rounded-lg overflow-hidden border">
                      {mediaFile.type === 'image' ? (
                        <img
                          src={mediaFile.preview}
                          alt="Preview"
                          className="w-full h-32 object-cover"
                        />
                      ) : (
                        <video
                          src={mediaFile.preview}
                          className="w-full h-32 object-cover"
                          controls
                        />
                      )}
                      
                      {/* Upload Progress */}
                      {uploadProgress[index] !== undefined && uploadProgress[index] < 100 && (
                        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                          <div className="text-white text-sm">
                            Uploading... {uploadProgress[index]}%
                          </div>
                        </div>
                      )}
                      
                      {/* Remove Button */}
                      <button
                        type="button"
                        onClick={() => removeMediaFile(index)}
                        className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                      >
                        ×
                      </button>
                    </div>
                    <p className="text-xs text-gray-500 mt-1 truncate">
                      {mediaFile.file.name}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Preview Toggle */}
          {content.trim() && (
            <div className="flex items-center space-x-4">
              <button
                type="button"
                onClick={() => setShowPreview(!showPreview)}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                {showPreview ? 'Hide Preview' : 'Show Preview'}
              </button>
            </div>
          )}

          {/* Post Preview */}
          {showPreview && content.trim() && (
            <div className="border rounded-lg p-4 bg-gray-50">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Preview:</h3>
              <div className="bg-white rounded p-3">
                <div 
                  className="text-gray-800 whitespace-pre-wrap"
                  dangerouslySetInnerHTML={{ __html: formatContent(content) }}
                />
                {mediaFiles.length > 0 && (
                  <div className="mt-3">
                    <div className="grid grid-cols-2 gap-2">
                      {mediaFiles.slice(0, 2).map((mediaFile, index) => (
                        <div key={index} className="rounded overflow-hidden">
                          {mediaFile.type === 'image' ? (
                            <img
                              src={mediaFile.preview}
                              alt="Preview"
                              className="w-full h-20 object-cover"
                            />
                          ) : (
                            <video
                              src={mediaFile.preview}
                              className="w-full h-20 object-cover"
                              muted
                            />
                          )}
                        </div>
                      ))}
                    </div>
                    {mediaFiles.length > 2 && (
                      <p className="text-xs text-gray-500 mt-1">
                        +{mediaFiles.length - 2} more files
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => {
                setContent('');
                setMediaFiles([]);
                setShowPreview(false);
                setError('');
                setSuccess('');
                if (textareaRef.current) {
                  textareaRef.current.style.height = 'auto';
                }
              }}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              disabled={isSubmitting}
            >
              Clear
            </button>
            
            <button
              type="submit"
              disabled={isSubmitting || !content.trim() || isOverLimit}
              className={`px-6 py-2 rounded-lg font-medium transition-colors duration-200 ${
                isSubmitting || !content.trim() || isOverLimit
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {isSubmitting ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Creating...</span>
                </div>
              ) : (
                'Create Post'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PostCreate; 