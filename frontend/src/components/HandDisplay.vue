<script setup>
import { ref } from 'vue';
import EditHandModal from './EditHandModal.vue';

// 親コンポーネント (App.vue) から手牌のデータを受け取る
defineProps({
    hand: {
        type: Array,
        required: true
    }
});

// 親コンポーネント (App.vue) に再計算イベントを伝える
const emit = defineEmits(['recalculate']);

const isEditModalVisible = ref(false);

/**
 * EditHandModalから 'save' イベントが来たら、
 * 'recalculate' イベントとして親に伝える
 * @param correctedHand - 修正後の手牌
 */
const handleHandUpdate = (correctedHand) => {
    isEditModalVisible.value = false;
    emit('recalculate', correctedHand); 
}

/**
 * 牌の名前（例: '1m'）を受け取り、対応する画像のパスを返す関数
 * @param {string} tileName - 牌の名前
 * @returns {string} - Viteが解決できる画像パス
 */
const getTileImage = (tileName) => {
    // 赤ドラ '5mr', '5pr', '5sr' も '5r' という画像ファイル名を参照するように修正
    if (tileName === '5mr' || tileName === '5pr' || tileName === '5sr') {
        tileName = '5r';
    }
    return new URL(`../assets/images/pai-images/${tileName}.png`, import.meta.url).href;
};
</script>

<template>
    <div class="hand-display">
        <div class="hand-header">
            <h3>認識された手牌</h3>
            <button class="edit-button" @click="isEditModalVisible = true">手牌を修正</button>
        </div>
        <div class="tiles">
            <img 
                v-for="(tile, index) in hand" 
                :key="index" 
                :src="getTileImage(tile)" 
                :alt="tile" 
                class="tile-image"
            />
        </div>
    </div>

    <!-- 手牌修正モーダル -->
    <EditHandModal
        v-if="isEditModalVisible"
        :initial-hand="hand"
        @close="isEditModalVisible = false"
        @save="handleHandUpdate"
    />
</template>

<style scoped>
/* ResultDisplay.vue から手牌表示に関連するスタイルのみを移動 */
.hand-display {
    margin-top: 2rem;
}

h3 {
    margin-bottom: 1rem;
    border-bottom: 2px solid #e8f0e8;
    padding-bottom: 0.5rem;
    color: #004d40;
}

.tiles {
    background-color: #f7f9f7;
    padding: 1rem;
    border-radius: 6px;
    font-size: 1.5rem;
    letter-spacing: 4px;
    text-align: center; /* 牌を中央揃えにする */
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
    transition: background-color 0.2s;
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
