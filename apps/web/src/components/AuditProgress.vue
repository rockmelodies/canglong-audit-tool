<template>
  <div class="audit-progress-panel" v-if="isVisible">
    <div class="progress-header">
      <div class="progress-title">
        <div class="pulse-indicator" :class="statusClass"></div>
        <h3>{{ title }}</h3>
      </div>
      <div class="progress-stats">
        <span class="stat-item">
          <span class="stat-label">{{ t('progress.files') }}:</span>
          <span class="stat-value">{{ processedFiles }}/{{ totalFiles }}</span>
        </span>
        <span class="stat-item">
          <span class="stat-label">{{ t('progress.findings') }}:</span>
          <span class="stat-value findings-count">{{ findingsCount }}</span>
        </span>
        <span class="stat-item">
          <span class="stat-label">{{ t('progress.time') }}:</span>
          <span class="stat-value">{{ formatTime(elapsedTime) }}</span>
        </span>
      </div>
    </div>
    
    <div class="progress-bar-container">
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: `${progressPercentage}%` }"
          :class="statusClass"
        ></div>
      </div>
      <div class="progress-percentage">{{ progressPercentage.toFixed(1) }}%</div>
    </div>
    
    <div class="current-task" v-if="currentTask">
      <div class="task-icon">🔍</div>
      <div class="task-info">
        <span class="task-name">{{ currentTask }}</span>
        <span class="task-file" v-if="currentFile">{{ currentFile }}</span>
      </div>
    </div>
    
    <div class="progress-stages" v-if="stages.length">
      <div 
        v-for="stage in stages" 
        :key="stage.name"
        class="stage-item"
        :class="getStageClass(stage.status)"
      >
        <div class="stage-icon">
          <span v-if="stage.status === 'completed'">✓</span>
          <span v-else-if="stage.status === 'running'" class="spinner"></span>
          <span v-else-if="stage.status === 'failed'">✕</span>
          <span v-else>○</span>
        </div>
        <div class="stage-info">
          <span class="stage-name">{{ stage.name }}</span>
          <span class="stage-detail" v-if="stage.detail">{{ stage.detail }}</span>
        </div>
        <div class="stage-time" v-if="stage.time">{{ formatTime(stage.time) }}</div>
      </div>
    </div>
    
    <div class="recent-findings" v-if="recentFindings.length">
      <h4>{{ t('progress.recentFindings') }}</h4>
      <div class="findings-list">
        <div 
          v-for="(finding, index) in recentFindings" 
          :key="index"
          class="finding-item"
          :class="`severity-${finding.severity}`"
        >
          <span class="finding-severity">{{ finding.severity.toUpperCase() }}</span>
          <span class="finding-title">{{ finding.title }}</span>
          <span class="finding-file">{{ finding.file }}:{{ finding.line }}</span>
        </div>
      </div>
    </div>
    
    <div class="progress-actions">
      <button 
        v-if="status === 'running'" 
        class="btn-pause"
        @click="pauseAudit"
      >
        {{ t('progress.pause') }}
      </button>
      <button 
        v-if="status === 'paused'" 
        class="btn-resume"
        @click="resumeAudit"
      >
        {{ t('progress.resume') }}
      </button>
      <button 
        v-if="status === 'completed' || status === 'failed'" 
        class="btn-close"
        @click="closeProgress"
      >
        {{ t('progress.close') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue';
import { useI18n } from '../i18n';

interface Stage {
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  detail?: string;
  time?: number;
}

interface Finding {
  severity: string;
  title: string;
  file: string;
  line: number;
}

const props = defineProps<{
  isVisible: boolean;
  title?: string;
  status: 'idle' | 'running' | 'paused' | 'completed' | 'failed';
  totalFiles: number;
  processedFiles: number;
  findingsCount: number;
  elapsedTime: number;
  currentTask?: string;
  currentFile?: string;
  stages: Stage[];
  recentFindings: Finding[];
}>();

const emit = defineEmits<{
  pause: [];
  resume: [];
  close: [];
}>();

const { t, locale } = useI18n();

const progressPercentage = computed(() => {
  if (props.totalFiles === 0) return 0;
  return (props.processedFiles / props.totalFiles) * 100;
});

const statusClass = computed(() => {
  return {
    'status-idle': props.status === 'idle',
    'status-running': props.status === 'running',
    'status-paused': props.status === 'paused',
    'status-completed': props.status === 'completed',
    'status-failed': props.status === 'failed'
  };
});

function getStageClass(status: string) {
  return `stage-${status}`;
}

function formatTime(seconds: number): string {
  if (seconds < 60) {
    return `${Math.floor(seconds)}s`;
  } else if (seconds < 3600) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${mins}m`;
  }
}

function pauseAudit() {
  emit('pause');
}

function resumeAudit() {
  emit('resume');
}

function closeProgress() {
  emit('close');
}
</script>

<style scoped>
.audit-progress-panel {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 20px;
  padding: 24px;
  border: 1px solid rgba(0, 212, 170, 0.2);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.progress-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-title h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #fff;
}

.pulse-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.pulse-indicator.status-running {
  background: #00d4aa;
}

.pulse-indicator.status-paused {
  background: #ffc107;
}

.pulse-indicator.status-completed {
  background: #28a745;
}

.pulse-indicator.status-failed {
  background: #dc3545;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.progress-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  gap: 6px;
  font-size: 0.9rem;
}

.stat-label {
  color: rgba(255, 255, 255, 0.6);
}

.stat-value {
  color: #fff;
  font-weight: 600;
}

.stat-value.findings-count {
  color: #ff6b6b;
}

.progress-bar-container {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-fill.status-running {
  background: linear-gradient(90deg, #00d4aa, #00b894);
}

.progress-fill.status-completed {
  background: linear-gradient(90deg, #28a745, #20c997);
}

.progress-fill.status-failed {
  background: linear-gradient(90deg, #dc3545, #c82333);
}

.progress-percentage {
  font-size: 0.9rem;
  font-weight: 600;
  color: #fff;
  min-width: 50px;
  text-align: right;
}

.current-task {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(0, 212, 170, 0.1);
  border-radius: 12px;
  margin-bottom: 20px;
}

.task-icon {
  font-size: 1.5rem;
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-name {
  color: #fff;
  font-weight: 500;
}

.task-file {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
}

.progress-stages {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.stage-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.stage-item.stage-running {
  background: rgba(0, 212, 170, 0.1);
  border-color: rgba(0, 212, 170, 0.3);
}

.stage-item.stage-completed {
  opacity: 0.7;
}

.stage-item.stage-failed {
  background: rgba(220, 53, 69, 0.1);
  border-color: rgba(220, 53, 69, 0.3);
}

.stage-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
}

.stage-item.stage-completed .stage-icon {
  color: #28a745;
}

.stage-item.stage-failed .stage-icon {
  color: #dc3545;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 212, 170, 0.3);
  border-top-color: #00d4aa;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.stage-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stage-name {
  color: #fff;
  font-size: 0.9rem;
}

.stage-detail {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
}

.stage-time {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
}

.recent-findings {
  margin-bottom: 20px;
}

.recent-findings h4 {
  margin: 0 0 12px;
  color: #fff;
  font-size: 0.95rem;
}

.findings-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.finding-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  font-size: 0.85rem;
}

.finding-item.severity-critical {
  border-left: 3px solid #dc3545;
}

.finding-item.severity-high {
  border-left: 3px solid #fd7e14;
}

.finding-item.severity-medium {
  border-left: 3px solid #ffc107;
}

.finding-item.severity-low {
  border-left: 3px solid #28a745;
}

.finding-severity {
  font-weight: 600;
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
}

.finding-item.severity-critical .finding-severity {
  color: #dc3545;
}

.finding-item.severity-high .finding-severity {
  color: #fd7e14;
}

.finding-item.severity-medium .finding-severity {
  color: #ffc107;
}

.finding-title {
  flex: 1;
  color: #fff;
}

.finding-file {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
}

.progress-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.progress-actions button {
  padding: 10px 20px;
  border-radius: 10px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-pause {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
  border: 1px solid rgba(255, 193, 7, 0.3);
}

.btn-pause:hover {
  background: rgba(255, 193, 7, 0.3);
}

.btn-resume {
  background: rgba(0, 212, 170, 0.2);
  color: #00d4aa;
  border: 1px solid rgba(0, 212, 170, 0.3);
}

.btn-resume:hover {
  background: rgba(0, 212, 170, 0.3);
}

.btn-close {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.15);
}
</style>
