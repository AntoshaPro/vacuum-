import React, { useState } from 'react';
import { SendRequest, SendResult } from '../api/types';

interface DestinationFormProps {
  selectedIds: number[];
  onSendComplete: (result: SendResult) => void;
}

const DestinationForm: React.FC<DestinationFormProps> = ({ selectedIds, onSendComplete }) => {
  const [destination, setDestination] = useState('');
  const [mode, setMode] = useState<'forward' | 'copy'>('forward');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedIds.length === 0) {
      setError('Пожалуйста, выберите хотя бы одно сообщение');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const requestData: SendRequest = {
        message_ids: selectedIds,
        dest: destination,
        mode: mode
      };
      
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: SendResult = await response.json();
      onSendComplete(result);
    } catch (err) {
      setError('Ошибка при отправке сообщений: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  if (selectedIds.length === 0) {
    return <div className="destination-form">Пожалуйста, сначала выберите сообщения для отправки</div>;
  }

  return (
    <div className="destination-form">
      <h3>Отправить выбранные (Send Selected)</h3>
      {error && <div className="error">Ошибка: {error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="destination">Назначение (пользователь или ID):</label>
          <input
            type="text"
            id="destination"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            placeholder="Имя пользователя или ID"
            required
          />
        </div>
        
        <div>
          <label>
            <input
              type="radio"
              name="mode"
              value="forward"
              checked={mode === 'forward'}
              onChange={() => setMode('forward')}
            />
            Переслать (Forward)
          </label>
          
          <label>
            <input
              type="radio"
              name="mode"
              value="copy"
              checked={mode === 'copy'}
              onChange={() => setMode('copy')}
            />
            Копировать (Copy)
          </label>
        </div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Отправка...' : 'Отправить (Send)'}
        </button>
      </form>
    </div>
  );
};

export default DestinationForm;