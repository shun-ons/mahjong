<script setup>
import { ref } from 'vue';

// 親コンポーネントから渡されるプロパティと、発行するイベントを定義
const props = defineProps({
    initialHand: {
        type: Array,
        required: true
    }
});
const emit = defineEmits(['close', 'save']);

// 編集用の手牌データ (プロパティを直接変更しないようにコピーを作成)
const editableHand = ref([...props.initialHand]);

// 牌選択パレットのデータ
const TILE_PALETTE = {
    '萬子(マンズ)': ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m'],
    '筒子(ピンズ)': ['1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p'],
    '索子(ソーズ)': ['1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s'],
    '字牌(ジハイ)': ['1z', '2z', '3z', '4z', '5z', '6z', '7z']
};

// どの牌を修正中か、または牌を追加中かを管理する状態
const editingIndex = ref(null); // 'add' または数値インデックス

// 画像パスを取得するヘルパー関数
const getTileImage = (tileName) => {
    return new URL(`../assets/images/pai-images/${tileName}.png`, import.meta.url).href;
};

// 牌の削除
const deleteTile = (index) => {
    editableHand.value.splice(index, 1);
};

// 牌の修正または追加を開始
const startEditing = (index) => {
    editingIndex.value = index;
};

// パレットから牌を選択して、修正または追加を実行
const selectTileFromPalette = (tile) => {
    if (editingIndex.value === 'add') {
        editableHand.value.push(tile);
    } else {
        editableHand.value[editingIndex.value] = tile;
    }
    editingIndex.value = null; // パレットを閉じる
};

// 変更を保存してモーダルを閉じる
const saveChanges = () => {
    if (editableHand.value.length > 14) {
        alert('手牌は14枚以下にしてください。');
        return;
    }
    emit('save', editableHand.value);
    };

</script>

<template>
    <div class="modal-overlay" @click.self="emit('close')">
        <div class="modal-content">
        <div class="modal-header">
            <h3>手牌を修正</h3>
            <p>牌の修正・追加・削除ができます。</p>
        </div>

        <div class="hand-editor">
            <div v-for="(tile, index) in editableHand" :key="index" class="tile-wrapper">
            <img :src="getTileImage(tile)" :alt="tile" class="tile-image" @click="startEditing(index)" />
            <button class="delete-btn" @click="deleteTile(index)">&times;</button>
            </div>
            <button class="add-btn" @click="startEditing('add')" v-if="editableHand.length < 14">+</button>
        </div>
        
        <div v-if="editingIndex !== null" class="palette-container">
            <h4>{{ editingIndex === 'add' ? '追加する牌を選択' : '修正後の牌を選択' }}</h4>
            <div v-for="(tiles, type) in TILE_PALETTE" :key="type" class="palette-group">
            <span class="palette-type">{{ type }}</span>
            <div class="palette-tiles">
                <img v-for="tile in tiles" :key="tile" :src="getTileImage(tile)" :alt="tile" class="palette-tile" @click="selectTileFromPalette(tile)" />
            </div>
            </div>
            <button class="palette-cancel-btn" @click="editingIndex = null">キャンセル</button>
        </div>

        <div class="modal-footer">
            <button class="cancel-btn" @click="emit('close')">キャンセル</button>
            <button class="save-btn" @click="saveChanges">この内容で再計算</button>
        </div>
    </div>
    </div>
</template>

<style scoped>
/* モーダル全体のスタイル */
.modal-overlay {
    position: fixed; top: 0; left: 0;
    width: 100%; height: 100%;
    background-color: rgba(0, 0, 0, 0.6);
    display: flex; justify-content: center; align-items: center; z-index: 1000;
}
.modal-content {
    background-color: #fff; padding: 2rem; border-radius: 8px;
    width: 90%; max-width: 700px; max-height: 90vh; overflow-y: auto;
}
.modal-header { text-align: center; margin-bottom: 1.5rem; }
.modal-header h3 { margin: 0; font-size: 1.5rem; }
.modal-header p { margin: 0.5rem 0 0; color: #555; }

/* 手牌エディタ */
.hand-editor { display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 10px; min-height: 80px; background-color: #f7f9f7; padding: 1rem; border-radius: 6px;}
.tile-wrapper { position: relative; }
.tile-image { height: 60px; cursor: pointer; transition: transform 0.2s; }
.tile-image:hover { transform: scale(1.05); }
.delete-btn {
    position: absolute; top: -8px; right: -8px;
    background-color: #d32f2f; color: white;
    border: none; border-radius: 50%;
    width: 24px; height: 24px;
    font-size: 1rem; font-weight: bold;
    cursor: pointer; display: flex; justify-content: center; align-items: center;
}
.add-btn {
    width: 42px; height: 60px;
    border: 2px dashed #ccc; border-radius: 4px;
    font-size: 2rem; color: #aaa;
    cursor: pointer; background-color: #fff;
}

/* 牌選択パレット */
.palette-container { margin-top: 1.5rem; padding: 1.5rem; border: 1px solid #eee; border-radius: 6px; }
.palette-group { margin-bottom: 1rem; }
.palette-type { font-weight: bold; font-size: 0.9rem; margin-bottom: 0.5rem; display: block; }
.palette-tiles { display: flex; flex-wrap: wrap; gap: 5px; }
.palette-tile { height: 48px; cursor: pointer; border-radius: 4px; }
.palette-tile:hover { box-shadow: 0 0 0 3px #00796b; }
.palette-cancel-btn { display: block; margin: 1rem auto 0; }

/* フッターボタン */
.modal-footer { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #eee; }
.cancel-btn, .save-btn { padding: 0.75rem 1.5rem; border: none; border-radius: 6px; font-size: 1rem; cursor: pointer; }
.cancel-btn { background-color: #f0f0f0; }
.save-btn { background-color: #004d40; color: white; }
</style>