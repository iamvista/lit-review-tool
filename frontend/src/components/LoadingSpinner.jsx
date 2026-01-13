/**
 * 全局加載指示器組件
 * Loading Spinner - 顯示加載動畫
 */

export default function LoadingSpinner({ size = 'medium', text = '載入中...' }) {
  const sizeClasses = {
    small: 'h-6 w-6 border-2',
    medium: 'h-12 w-12 border-2',
    large: 'h-16 w-16 border-4'
  }

  const sizeClass = sizeClasses[size] || sizeClasses.medium

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div
        className={`${sizeClass} border-indigo-200 border-t-indigo-600 rounded-full animate-spin`}
      ></div>
      {text && (
        <p className="mt-4 text-gray-600 text-sm">{text}</p>
      )}
    </div>
  )
}

/**
 * 全頁加載指示器
 */
export function FullPageLoading({ text = '載入中...' }) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <LoadingSpinner size="large" text={text} />
    </div>
  )
}

/**
 * 內聯加載指示器（用於按鈕等）
 */
export function InlineLoading({ text = '處理中...' }) {
  return (
    <span className="inline-flex items-center">
      <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
      {text}
    </span>
  )
}
