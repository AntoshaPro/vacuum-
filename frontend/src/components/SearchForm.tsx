import React, { useState } from 'react';
import { SearchRequest } from '../api/types';

interface SearchFormProps {
  onSearch: (searchParams: SearchRequest) => void;
  loading: boolean;
}

const SearchForm: React.FC<SearchFormProps> = ({ onSearch, loading }) => {
  const [fromDate, setFromDate] = useState<string>('');
  const [toDate, setToDate] = useState<string>('');
  const [limitPerDialog, setLimitPerDialog] = useState<number | undefined>(undefined);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch({
      from_date: fromDate ? fromDate + 'T00:00:00' : undefined,
      to_date: toDate ? toDate + 'T23:59:59' : undefined,
      limit_per_dialog: limitPerDialog ? parseInt(limitPerDialog.toString()) : undefined,
    });
  };

  return (
    <div className="search-form">
      <h3>Поиск благодарностей (Search for Thanks)</h3>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="from-date">Дата начала (From date):</label>
          <input
            type="date"
            id="from-date"
            value={fromDate}
            onChange={(e) => setFromDate(e.target.value)}
          />
        </div>
        
        <div>
          <label htmlFor="to-date">Дата окончания (To date):</label>
          <input
            type="date"
            id="to-date"
            value={toDate}
            onChange={(e) => setToDate(e.target.value)}
          />
        </div>
        
        <div>
          <label htmlFor="limit-per-dialog">Ограничение на диалог (Limit per dialog):</label>
          <input
            type="number"
            id="limit-per-dialog"
            value={limitPerDialog || ''}
            onChange={(e) => setLimitPerDialog(e.target.value ? parseInt(e.target.value) : undefined)}
            placeholder="неограниченно"
          />
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Поиск...' : 'Запустить поиск (Search)'}
        </button>
      </form>
    </div>
  );
};

export default SearchForm;