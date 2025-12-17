import React, { useState } from 'react';
import ConfigForm from '../components/ConfigForm';
import KeywordsEditor from '../components/KeywordsEditor';
import SearchForm from '../components/SearchForm';
import ResultsTable from '../components/ResultsTable';
import DestinationForm from '../components/DestinationForm';
import apiClient from '../api/client';
import { ThankMessage, SearchRequest, SendResult } from '../api/types';

const MainPage: React.FC = () => {
  const [messages, setMessages] = useState<ThankMessage[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [sendResult, setSendResult] = useState<SendResult | null>(null);
  const [status, setStatus] = useState<string>('');

  // Загрузка статуса приложения
  React.useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await apiClient.get('/api/status');
        setStatus(response.data.message);
      } catch (err) {
        setStatus('Ошибка соединения с сервером');
      }
    };
    fetchStatus();
  }, []);

  const handleSearch = async (params: SearchRequest) => {
    setSearchLoading(true);
    setSendResult(null);
    try {
      const response = await apiClient.post('/api/search', params);
      setMessages(response.data);
      setSelectedIds([]);
    } catch (err) {
      console.error('Ошибка поиска:', err);
      alert('Ошибка при поиске сообщений: ' + (err as Error).message);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleSendComplete = (result: SendResult) => {
    setSendResult(result);
    // Очищаем выделенные сообщения после отправки
    setSelectedIds([]);
  };

  return (
    <div className="main-page">
      <h1>Благодарности из Telegram (Telegram Thanks Extractor)</h1>
      <p>Статус: {status}</p>

      <div className="section">
        <ConfigForm onConfigUpdate={() => {}} />
      </div>

      <div className="section">
        <KeywordsEditor onKeywordsUpdate={() => {}} />
      </div>

      <div className="section">
        <SearchForm onSearch={handleSearch} loading={searchLoading} />
      </div>

      <div className="section">
        <h3>Результаты поиска (Search Results)</h3>
        <ResultsTable 
          messages={messages} 
          selectedIds={selectedIds} 
          onSelectionChange={setSelectedIds} 
        />
      </div>

      <div className="section">
        <DestinationForm 
          selectedIds={selectedIds} 
          onSendComplete={handleSendComplete} 
        />
        {sendResult && (
          <div className={`send-result ${sendResult.success ? 'success' : 'error'}`}>
            <h4>Результат отправки:</h4>
            <p>Успешно: {sendResult.successful}, Неудачно: {sendResult.failed}</p>
            {sendResult.errors.length > 0 && (
              <div>
                <h5>Ошибки:</h5>
                <ul>
                  {sendResult.errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MainPage;