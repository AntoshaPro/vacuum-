import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { Config } from '../api/types';

interface ConfigFormProps {
  onConfigUpdate: () => void;
}

const ConfigForm: React.FC<ConfigFormProps> = ({ onConfigUpdate }) => {
  const [config, setConfig] = useState<Config | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/config');
      setConfig(response.data);
    } catch (err) {
      setError('Не удалось загрузить конфигурацию: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    if (config) {
      setConfig({
        ...config,
        [name]: name === 'TG_API_ID' ? parseInt(value) : value,
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/api/config', config);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      onConfigUpdate(); // Уведомляем родителя об обновлении
    } catch (err) {
      setError('Не удалось сохранить конфигурацию: ' + (err as Error).message);
    }
  };

  if (loading) return <div>Загрузка конфигурации...</div>;
  if (error) return <div className="error">Ошибка: {error}</div>;

  return (
    <div className="config-form">
      <h3>Конфигурация (Configuration)</h3>
      {success && <div className="success">Конфигурация успешно обновлена!</div>}
      
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="TG_API_ID">TG_API_ID:</label>
          <input
            type="number"
            id="TG_API_ID"
            name="TG_API_ID"
            value={config?.TG_API_ID || ''}
            onChange={handleChange}
            required
          />
        </div>
        
        <div>
          <label htmlFor="TG_API_HASH">TG_API_HASH:</label>
          <input
            type="password"
            id="TG_API_HASH"
            name="TG_API_HASH"
            value={config?.TG_API_HASH || ''}
            onChange={handleChange}
            required
          />
        </div>
        
        <div>
          <label htmlFor="TG_SESSION_NAME">TG_SESSION_NAME:</label>
          <input
            type="text"
            id="TG_SESSION_NAME"
            name="TG_SESSION_NAME"
            value={config?.TG_SESSION_NAME || ''}
            onChange={handleChange}
          />
        </div>
        
        <div>
          <label htmlFor="OUTPUT_FILE">OUTPUT_FILE:</label>
          <input
            type="text"
            id="OUTPUT_FILE"
            name="OUTPUT_FILE"
            value={config?.OUTPUT_FILE || ''}
            onChange={handleChange}
          />
        </div>
        
        <div>
          <label htmlFor="KEYWORDS_FILE">KEYWORDS_FILE:</label>
          <input
            type="text"
            id="KEYWORDS_FILE"
            name="KEYWORDS_FILE"
            value={config?.KEYWORDS_FILE || ''}
            onChange={handleChange}
          />
        </div>
        
        <button type="submit">Сохранить (Save)</button>
      </form>
    </div>
  );
};

export default ConfigForm;