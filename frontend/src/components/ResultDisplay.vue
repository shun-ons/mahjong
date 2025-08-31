<script setup>
import { ref } from 'vue';
import EditHandModal from './EditHandModal.vue';

// App.vueから渡されるデータ（プロパティ）を定義
defineProps({
    result: {
        type: Object,
        required: true
    }
    });
const emit = defineEmits(['recalculate'])
const isEditModalVisible = ref(false);

/**
 * App.vueに再計算を依頼するためのハンドラ関数.
 * @param correctedHand - 修正後の手牌.
 */
const handleHandUpdate = (correctedHand) => {
    isEditModalVisible.value = false;
    emit('recalculate', correctedHand); 
}

/**
 * 牌の名前（例: '1m'）を受け取り、対応する画像のパスを返す関数.
 * @param {string} tileName - 牌の名前.
 * @returns {string} - Vite/Webpackが解決できる画像パス.
 */
const getTileImage = (tileName) => {
    return new URL(`../assets/images/pai-images/${tileName}.png`, import.meta.url).href;
};
</script>

<template>
    <div class="result-container">
        <h2>計算結果</h2>
        
        <div class="score-display">
            <span class="score-name">{{ result.score_name }}</span>
            <span class="score-points">{{ result.total }} 点</span>
            <div v-if="result.payment_from_oya">
                <span class="score-name">親の支払い: </span>
                <span class="score-points">{{ result.payment_from_oya }} 点</span>
            </div>
            <div v-if="result.payment_per_ko">
                <span class="score-name">子の支払い: </span>
                <span class="score-points">{{ result.payment_per_ko }} 点</span>
            </div>
            <div v-if="result.payment_from_ron">
                <span class="score-name">ロンの支払い: </span>
                <span class="score-points">{{ result.payment_from_ron }} 点</span>
            </div>
        </div>

        <div class="details-grid">
            <div class="detail-item">
                <span class="label">翻数</span>
                <span class="value">{{ result.han }} 飜</span>
            </div>
            <div class="detail-item">
                <span class="label">符</span>
                <span class="value">{{ result.fu }} 符</span>
            </div>
        </div>

        <div class="yaku-list">
        <h3 class="yaku-title">成立役</h3>
        <ul>
            <li v-for="(han, yaku) in result.yaku" :key="yaku">
                {{ yaku }} <span class="yaku-han">({{ han }}飜)</span>
            </li>
        </ul>
        </div>

        <div class="hand-display">
        <h3>和了手牌</h3>
        <div class="hand-header">
            <button class="edit-button" @click="isEditModalVisible = true">手牌を修正</button>
        </div>
        <div class="tiles">
            <img 
                v-for="(tile, index) in result.hand" 
                :key="index" 
                :src="getTileImage(tile)" 
                :alt="tile" 
                class="tile-image"
            />
        </div>
        </div>
    </div>

    <EditHandModal
        v-if="isEditModalVisible"
        :initial-hand="result.hand"
        @close="isEditModalVisible = false"
        @save="handleHandUpdate"
    />
</template>

<style scoped>
.result-container {
    margin-top: 2rem;
    padding: 2rem;
    border: 1px solid #dce5dc;
    border-radius: 8px;
    background-color: #fff;
    animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

h2 {
    text-align: center;
    color: #004d40;
    font-size: 2rem;
    margin-top: 0;
    margin-bottom: 1.5rem;
}

.score-display {
    text-align: center;
    margin-bottom: 2rem;
    padding: 1rem;
    background-color: #e8f0e8;
    border-radius: 6px;
}

.score-name {
    font-size: 1.5rem;
    font-weight: 500;
    margin-right: 1rem;
}

.score-points {
    font-size: 2.2rem;
    font-weight: bold;
    color: #004d40;
}

.details-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 2rem;
    text-align: center;
}

.detail-item .label {
    display: block;
    font-size: 1rem;
    color: #556b55;
    margin-bottom: 0.25rem;
}

.detail-item .value {
    font-size: 1.5rem;
    font-weight: 500;
}

.yaku-list ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.yaku-list li {
    background-color: #f7f9f7;
    border: 1px solid #dce5dc;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 1rem;
}
.yaku-han {
    color: #00796b;
    font-weight: bold;
}

.hand-display {
    margin-top: 2rem;
}

h3 {
    margin-bottom: 1rem;
    border-bottom: 2px solid #e8f0e8;
    padding-bottom: 0.5rem;
}

.tiles {
    background-color: #f7f9f7;
    padding: 1rem;
    border-radius: 6px;
    font-size: 1.5rem;
    letter-spacing: 4px;
}

.tile-image {
    height: 48px;
    margin: 0 2px;
    vertical-align: middle;
}

.hand-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    border-bottom: 2px solid #e8f0e8;
    padding-bottom: 0.5rem;
}
.hand-header h3 {
    margin: 0;
    padding: 0;
    border: none;
}
.edit-button {
    padding: 0.5rem 1rem;
    background-color: #fff;
    border: 1px solid #00796b;
    color: #00796b;
    border-radius: 6px;
    cursor: pointer;
}
.edit-button:hover {
    background-color: #e8f0e8;
}
.tile-image {
    height: 48px;
    margin: 0 2px;
    vertical-align: middle;
}
</style>