import React, { useState } from 'react';
import { ThankMessage } from '../api/types';

interface ResultsTableProps {
  messages: ThankMessage[];
  selectedIds: number[];
  onSelectionChange: (ids: number[]) => void;
}

const ResultsTable: React.FC<ResultsTableProps> = ({ messages, selectedIds, onSelectionChange }) => {
  const [selectAll, setSelectAll] = useState(false);

  const handleCheckboxChange = (id: number) => {
    if (selectedIds.includes(id)) {
      onSelectionChange(selectedIds.filter(msgId => msgId !== id));
    } else {
      onSelectionChange([...selectedIds, id]);
    }
  };

  const handleSelectAll = () => {
    if (selectAll) {
      onSelectionChange([]);
    } else {
      onSelectionChange(messages.map(msg => msg.id));
    }
    setSelectAll(!selectAll);
  };

  const handleDeselectAll = () => {
    onSelectionChange([]);
    setSelectAll(false);
  };

  return (
    <div className="results-table">
      <div className="table-actions">
        <button onClick={handleSelectAll}>
          {selectAll ? 'Снять выбор (Deselect all)' : 'Выбрать все (Select all)'}
        </button>
        <button onClick={handleDeselectAll}>Снять выбор (Deselect all)</button>
      </div>
      
      <table>
        <thead>
          <tr>
            <th>Выбрать</th>
            <th>Дата</th>
            <th>Чат</th>
            <th>Пользователь</th>
            <th>Текст</th>
          </tr>
        </thead>
        <tbody>
          {messages.length === 0 ? (
            <tr>
              <td colSpan={5}>Сообщения не найдены</td>
            </tr>
          ) : (
            messages.map((msg) => (
              <tr key={msg.id}>
                <td>
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(msg.id)}
                    onChange={() => handleCheckboxChange(msg.id)}
                  />
                </td>
                <td>{new Date(msg.date).toLocaleString()}</td>
                <td>{msg.chat_name}</td>
                <td>{msg.username ? `@${msg.username}` : 'N/A'}</td>
                <td>{msg.text}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default ResultsTable;