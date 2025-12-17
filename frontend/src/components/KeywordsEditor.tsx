import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';

interface KeywordsEditorProps {
  onKeywordsUpdate: () => void;
}

const KeywordsEditor: React.FC<KeywordsEditorProps> = ({ onKeywordsUpdate }) => {
  const [keywords, setKeywords] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchKeywords();
  }, []);

  const fetchKeywords = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/keywords');
      setKeywords(response.data.keywords);
    } catch (err) {
      setError('Не удалось загрузить ключевые слова: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = e.target.value;
    // Разделяем по новым строкам и фильтруем пустые строки
    const newKeywords = text.split('\n').filter(kw => kw.trim() !== '');
    setKeywords(newKeywords);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/api/keywords', keywords);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      onKeywordsUpdate(); // Уведомляем родителя об обновлении
    } catch (err) {
      setError('Не удалось сохранить ключевые слова: ' + (err as Error).message);
    }
  };

  if (loading) return <div>Загрузка ключевых слов...</div>;
  if (error) return <div className="error">Ошибка: {error}</div>;

  return (
    <div className="keywords-editor">
      <h3>Редактор ключевых слов (Keywords Editor)</h3>
      {success && <div className="success">Ключевые слова успешно обновлены!</div>}
      
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="keywords">Ключевые слова (по одному на строку):</label>
          <textarea
            id="keywords"
            value={keywords.join('\n')}
            onChange={handleTextChange}
            rows={10}
            cols={50}
            placeholder="Введите ключевые слова по одному на строку..."
          />
        </div>
        <button type="submit">Сохранить (Save)</button>
      </form>
    </div>
  );
};

export default KeywordsEditor;