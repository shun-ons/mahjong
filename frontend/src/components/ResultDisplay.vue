<script setup>
// import { ref } from 'vue'; // 削除
// import EditHandModal from './EditHandModal.vue'; // 削除
// import HandDisplay from './HandDisplay.vue'; // 削除 (App.vueで読み込む)

// App.vueから渡されるデータ（プロパティ）を定義
defineProps({
    result: {
        type: Object,
        required: true
    }
});

// App.vueに 'recalculate' イベントを中継する必要がなくなったため削除
// const emit = defineEmits(['recalculate'])

// isEditModalVisible は削除
// const isEditModalVisible = ref(false);

// handleHandUpdate は削除
// const handleHandUpdate = (correctedHand) => { ... }

// getTileImage は削除
// const getTileImage = (tileName) => { ... };

// onRecalculate は削除
// const onRecalculate = (correctedHand) => { ... }
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
                    {{ yaku + 1}} <span class="yaku-han">({{ han }})</span>
                </li>
            </ul>
        </div>

        <!-- 手牌表示のセクション (hand-display) はここから削除 -->

    </div>

    <!-- EditHandModal の呼び出しも削除 -->
</template>

<style scoped>
/* スタイルは ResultDisplay に関連するものだけを残す */
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

h3 { /* yaku-list のために h3 は残す */
    margin-bottom: 1rem;
    border-bottom: 2px solid #e8f0e8;
    padding-bottom: 0.5rem;
    color: #004d40;
}

/* .hand-display 以下のスタイルはすべて削除 */
</style>
