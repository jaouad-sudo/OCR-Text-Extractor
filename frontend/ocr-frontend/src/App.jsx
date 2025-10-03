import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Upload, FileText, Image, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'
import './App.css'

function App() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [extractedText, setExtractedText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [fileType, setFileType] = useState('')
  const [previewUrl, setPreviewUrl] = useState('')
  const fileInputRef = useRef(null)

  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
  const maxFileSize = 16 * 1024 * 1024 // 16MB

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (!file) return

    // Reset previous states
    setError('')
    setSuccess('')
    setExtractedText('')
    setPreviewUrl('')

    // Validate file type
    if (!allowedTypes.includes(file.type)) {
      setError('Please select a valid file type (JPG, PNG, or PDF)')
      return
    }

    // Validate file size
    if (file.size > maxFileSize) {
      setError('File size must be less than 16MB')
      return
    }

    setSelectedFile(file)

    // Create preview for images
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => setPreviewUrl(e.target.result)
      reader.readAsDataURL(file)
    }
  }

  const handleDragOver = (event) => {
    event.preventDefault()
  }

  const handleDrop = (event) => {
    event.preventDefault()
    const files = event.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      // Simulate file input change
      const fakeEvent = { target: { files: [file] } }
      handleFileSelect(fakeEvent)
    }
  }

  const extractText = async () => {
    if (!selectedFile) {
      setError('Please select a file first')
      return
    }

    setIsLoading(true)
    setError('')
    setSuccess('')

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await fetch('/api/extract-text', {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (data.success) {
        setExtractedText(data.text)
        setFileType(data.file_type)
        setSuccess(`Text extracted successfully from ${data.file_type}!`)
      } else {
        setError(data.error || 'Failed to extract text')
      }
    } catch (err) {
      setError('Network error: Unable to connect to the server')
    } finally {
      setIsLoading(false)
    }
  }

  const clearAll = () => {
    setSelectedFile(null)
    setExtractedText('')
    setError('')
    setSuccess('')
    setFileType('')
    setPreviewUrl('')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(extractedText)
      setSuccess('Text copied to clipboard!')
    } catch (err) {
      setError('Failed to copy text to clipboard')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-900 flex items-center justify-center gap-3">
            <FileText className="h-10 w-10 text-blue-600" />
            OCR Text Extractor
          </h1>
          <p className="text-lg text-gray-600">
            Extract text from images and PDF files using advanced OCR technology
          </p>
        </div>

        {/* File Upload Section */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Upload File
            </CardTitle>
            <CardDescription>
              Select an image (JPG, PNG) or PDF file to extract text from. Maximum file size: 16MB.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Drag and Drop Area */}
            <div
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-lg font-medium text-gray-700 mb-2">
                Drop your file here or click to browse
              </p>
              <p className="text-sm text-gray-500">
                Supports JPG, PNG, and PDF files up to 16MB
              </p>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept=".jpg,.jpeg,.png,.pdf"
              onChange={handleFileSelect}
              className="hidden"
            />

            {/* Selected File Info */}
            {selectedFile && (
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {selectedFile.type.startsWith('image/') ? (
                      <Image className="h-5 w-5 text-blue-600" />
                    ) : (
                      <FileText className="h-5 w-5 text-red-600" />
                    )}
                    <div>
                      <p className="font-medium text-gray-900">{selectedFile.name}</p>
                      <p className="text-sm text-gray-600">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <Badge variant="secondary">
                    {selectedFile.type.startsWith('image/') ? 'Image' : 'PDF'}
                  </Badge>
                </div>
              </div>
            )}

            {/* Image Preview */}
            {previewUrl && (
              <div className="mt-4">
                <p className="text-sm font-medium text-gray-700 mb-2">Preview:</p>
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="max-w-full max-h-64 object-contain rounded-lg border"
                />
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3">
              <Button
                onClick={extractText}
                disabled={!selectedFile || isLoading}
                className="flex-1"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Extracting Text...
                  </>
                ) : (
                  <>
                    <FileText className="h-4 w-4 mr-2" />
                    Extract Text
                  </>
                )}
              </Button>
              <Button variant="outline" onClick={clearAll}>
                Clear All
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Alerts */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">{success}</AlertDescription>
          </Alert>
        )}

        {/* Extracted Text Section */}
        {extractedText && (
          <Card className="shadow-lg">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Extracted Text
                  {fileType && (
                    <Badge variant="outline" className="ml-2">
                      {fileType.toUpperCase()}
                    </Badge>
                  )}
                </CardTitle>
                <Button variant="outline" size="sm" onClick={copyToClipboard}>
                  Copy to Clipboard
                </Button>
              </div>
              <CardDescription>
                The text extracted from your file is displayed below.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
                <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                  {extractedText}
                </pre>
              </div>
              <div className="mt-4 text-sm text-gray-600">
                Character count: {extractedText.length}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Footer */}
        <div className="text-center text-sm text-gray-500">
          <p>Powered by Tesseract OCR and advanced PDF processing</p>
        </div>
      </div>
    </div>
  )
}

export default App
