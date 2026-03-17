<template>
  <section class="panel">
    <div class="section-heading">
      <div>
        <p class="eyebrow">Activity Feed</p>
        <h2>Latest mission evidence</h2>
      </div>
      <span class="capsule">Live cadence</span>
    </div>

    <div class="feed-list">
      <article v-for="event in items" :key="`${event.time}-${event.title}`" class="feed-item">
        <span class="feed-time">{{ event.time }}</span>
        <div>
          <div class="feed-headline">
            <strong>{{ event.title }}</strong>
            <span class="capsule">{{ event.tag }}</span>
          </div>
          <p>{{ event.detail }}</p>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { FeedEvent } from '../types';

defineProps<{
  items: FeedEvent[];
}>();
</script>

<style scoped>
.section-heading {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.section-heading h2 {
  margin: 8px 0 0;
}

.feed-list {
  display: grid;
  gap: 16px;
  margin-top: 24px;
}

.feed-item {
  display: grid;
  grid-template-columns: 64px minmax(0, 1fr);
  gap: 16px;
  padding: 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.feed-time {
  color: var(--accent);
  font-weight: 700;
}

.feed-headline {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.feed-item p {
  margin-bottom: 0;
  color: var(--text-dim);
}

@media (max-width: 620px) {
  .feed-item {
    grid-template-columns: 1fr;
  }
}
</style>

