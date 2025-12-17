// Типы для API

export interface Config {
  TG_API_ID: number;
  TG_API_HASH: string;
  TG_SESSION_NAME: string;
  OUTPUT_FILE: string;
  KEYWORDS_FILE: string;
}

export interface ThankMessage {
  id: number;
  chat_id: number;
  chat_name: string;
  username: string | null;
  date: string; // ISO строка даты
  text: string;
  peer_type: string; // 'user', 'chat', 'channel'
}

export interface SearchRequest {
  from_date?: string;
  to_date?: string;
  limit_per_dialog?: number;
}

export interface SendRequest {
  message_ids: number[];
  dest: string;
  mode: 'forward' | 'copy';
}

export interface SendResult {
  success: boolean;
  successful: number;
  failed: number;
  total_processed: number;
  errors: string[];
}

export interface StatusResponse {
  status: string;
  version: string;
  telegram_connected: boolean;
  message: string;
}