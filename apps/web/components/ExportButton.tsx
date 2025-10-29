'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Download, FileSpreadsheet, FileJson, Calendar, FileText } from 'lucide-react'
import { exportToExcel, exportToCSV, exportToICal, exportToJSON, ExportEvent } from '@/lib/exportUtils'

interface ExportButtonProps {
  data: ExportEvent[]
  filename?: string
  label?: string
  variant?: 'default' | 'outline' | 'ghost' | 'secondary'
  size?: 'default' | 'sm' | 'lg'
}

export function ExportButton({ 
  data, 
  filename = 'agi-tracker-export', 
  label = 'Export',
  variant = 'outline',
  size = 'sm'
}: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false)
  
  const handleExport = async (format: 'excel' | 'csv' | 'ical' | 'json') => {
    setIsExporting(true)
    
    try {
      switch (format) {
        case 'excel':
          exportToExcel(data, filename)
          break
        case 'csv':
          exportToCSV(data, filename)
          break
        case 'ical':
          exportToICal(data, filename)
          break
        case 'json':
          exportToJSON(data, filename)
          break
      }
    } catch (error) {
      console.error('Export failed:', error)
      alert('Export failed. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }
  
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant={variant} size={size} disabled={isExporting || data.length === 0}>
          <Download className="w-4 h-4 mr-2" />
          {isExporting ? 'Exporting...' : label}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>Export Format</DropdownMenuLabel>
        <DropdownMenuSeparator />
        
        <DropdownMenuItem onClick={() => handleExport('excel')}>
          <FileSpreadsheet className="w-4 h-4 mr-2 text-green-600" />
          Excel (.xlsx)
        </DropdownMenuItem>
        
        <DropdownMenuItem onClick={() => handleExport('csv')}>
          <FileText className="w-4 h-4 mr-2 text-blue-600" />
          CSV (.csv)
        </DropdownMenuItem>
        
        <DropdownMenuItem onClick={() => handleExport('ical')}>
          <Calendar className="w-4 h-4 mr-2 text-purple-600" />
          Calendar (.ics)
        </DropdownMenuItem>
        
        <DropdownMenuItem onClick={() => handleExport('json')}>
          <FileJson className="w-4 h-4 mr-2 text-orange-600" />
          JSON (.json)
        </DropdownMenuItem>
        
        <DropdownMenuSeparator />
        
        <div className="px-2 py-1.5 text-xs text-muted-foreground">
          {data.length} item{data.length !== 1 ? 's' : ''} to export
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

