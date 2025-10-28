<script setup>
import { ref, computed } from 'vue';
import ResultDisplay from './components/ResultDisplay.vue';
import HandDisplay from './components/HandDisplay.vue'; // ★ HandDisplay をインポート

// 送信データを定義.
const formData = ref({
  image: null,
  is_tsumo: true,
  is_oya: false,
  dora_indicators: '',
  ura_dora_indicators: '',
  agari_hai: '',
  bakaze: '1z',
  jikaze: '1z',
  renchan: 0,
  is_chankan: false,
  is_haitei: false,
  is_houtei: false,
  is_ippatsu: false,
  is_riichi: false,
  is_double_riichi: false,
  is_tenhou: false,
  is_chiihou: false,
  is_rinshan: false,
  called_mentsu_list: []
});

// 状態管理用の変数を定義.
const calculationResult = ref(null); // 点数計算結果を保持
const recognizedHand = ref(null);      // ★ 認識された手牌を保持
const isLoading = ref(false);        // 通信中かどうか
const errorState = ref(null);        // エラーメッセージ

// (モーダル関連のコードは変更なし)
const isModalVisible = ref(false); 
const openModal = () => { isModalVisible.value = true; };
const closeModal = () => { isModalVisible.value = false; };

// (ファイル選択、面前、鳴き情報のコードも変更なし)
const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    formData.value.image = file;
  }
};
const isMenzen = computed(() => {
  return formData.value.called_mentsu_list.length === 0;
});
const addMeld = () => {
  formData.value.called_mentsu_list.push({type: 'pon', tiles: ''});
};
const removeMeld = (index) => {
  formData.value.called_mentsu_list.splice(index, 1);
};


// データ送信用の関数
const sendData = () => {
  // 状態をリセット.
  isLoading.value = true;
  errorState.value = null;
  calculationResult.value = null; // ★ 点数結果をクリア
  recognizedHand.value = null;    // ★ 手牌もクリア

  // (submissionData の作成は変更なし)
  const submissionData = new FormData();
  if (formData.value.image) {
    submissionData.append('image', formData.value.image);
  }
  const gameInfo = {};
  for (const key in formData.value) {
    if (key !== 'image') {
      gameInfo[key] = formData.value[key];
    }
  }
  gameInfo.is_menzen = isMenzen.value;
  submissionData.append('game_info', JSON.stringify(gameInfo));

  fetch('/api/calculate', {
    method: 'POST',
    body: submissionData,
  })
  .then(result => {
    // ★ エラーレスポンスからもJSONをパース試行
    if (!result.ok) {
        // エラーJSONをパースして、元のErrorオブジェクトにdataプロパティとして追加
        return result.json().then(errData => {
            const error = new Error(errData.message || 'サーバーエラーが発生しました');
            error.data = errData; // ★ エラーデータ（手牌が含まれる可能性）を添付
            throw error;
        });
    }
    return result.json();
  })
  .then(result => {
    if (result.status === 'success') {
      calculationResult.value = result.data; // ★ 点数結果をセット
      recognizedHand.value = result.data.hand;  // ★ 認識された手牌をセット
      errorState.value = null; // エラーをクリア
    } else {
      // APIがステータス200でエラーを返した場合
      const error = new Error(result.message || 'サーバーエラーが発生しました');
      error.data = result.data; // ★ 手牌データが含まれている可能性
      throw error;
    }
  })
  .catch(error => {
    errorState.value = error.message;
    calculationResult.value = null; // 失敗したら点数結果はクリア
    
    // ★ バックエンドがエラー時も手牌を返してくれていれば、ここでセット
    if (error.data && error.data.hand) {
      recognizedHand.value = error.data.hand;
    } else {
      recognizedHand.value = null; // 手牌がなければクリア
    }
    console.error('There was a problem with the fetch operation:', error);
  })
  .finally(() => {
    isLoading.value = false;
  });
}

const recalculateScore = (correctedHand) => {
  isLoading.value = true;
  errorState.value = null;
  calculationResult.value = null; // ★ 点数結果を一旦クリア
  recognizedHand.value = correctedHand; // ★ 修正後の手牌は表示し続ける

  // (game_info の作成は変更なし)
  const game_info = {};
  for (const key in formData.value) {
    if (key !== 'image') {
      game_info[key] = formData.value[key];
    }
  }
  game_info.is_menzen = formData.value.called_mentsu_list.length === 0;
  game_info.hand = correctedHand; // ★ 修正後の手牌を使う

  fetch('/api/calculate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({game_info: game_info}),
  })
  .then(result => {
    if (!result.ok) {
      return result.json().then(err => { 
        const error = new Error(err.message || 'サーバーエラーが発生しました');
        error.data = err; // エラーレスポンスを添付
        throw error;
      });
    }
    return result.json();
  })
  .then(result => {
    if (result.status === 'success') {
      calculationResult.value = result.data;
      recognizedHand.value = result.data.hand; // 念のため手牌も更新
      errorState.value = null;
    } else {
      const error = new Error(result.message || 'サーバーエラーが発生しました');
      error.data = result.data;
      throw error;
    }
  })
  .catch(error => {
    errorState.value = error.message;
    calculationResult.value = null; // 点数計算は失敗
    // ★ でも recognizedHand.value はクリアしない！
    
    // ★ もしバックエンドがエラー時に手牌を返してくれたら更新
    if (error.data && error.data.hand) {
      recognizedHand.value = error.data.hand;
    }
    
    console.error('There was a problem with the fetch operation:', error);
  })
  .finally(() => {
    isLoading.value = false;
  });
};
</script>

<template>
  <div class="container">
    <header>
      <h1>麻雀得点計算サイト</h1>
      <p>このサイトでは、麻雀の得点計算を行うことができます。<br>以下のフォームに手牌の画像と情報を入力してください</p>
    </header>

    <main>
      <!-- フォーム部分は変更なし -->
      <form @submit.prevent="sendData" method="post" class="score-form">
        <!-- (fieldset ... ) -->
        <fieldset>
          <legend>基本情報</legend>
          <div class="form-group">
            <label for="image">手牌の画像:</label>
            <input type="file" id="image" name="image" accept="image/*" @change="handleFileChange" required>
          </div>
          <div class="form-group">
            <label for="is_tsumo">和了り方:</label>
            <select id="is_tsumo" name="is_tsumo" v-model="formData.is_tsumo" required>
                <option :value="true">ツモ</option>
                <option :value="false">ロン</option>
            </select>
          </div>
          <div class="form-group">
            <label for="is_oya">親/子:</label>
            <select id="is_oya" name="is_oya" v-model="formData.is_oya" required>
                <option :value="true">親</option>
                <option :value="false">子</option>
            </select>
          </div>
          </fieldset>

        <fieldset>
          <legend>ドラ情報</legend>
          <p>カンマ区切りで記述してください.</p>
          <div class="form-group">
            <label for="dora_indicators">ドラ:</label>
            <input type="text" id="dora_indicators" name="dora_indicators" placeholder="例: 5m, 2p" v-model="formData.dora_indicators">
          </div>
          <div class="form-group">
            <label for="ura_dora_indicators">裏ドラ:</label>
            <input type="text" id="ura_dora_indicators" name="ura_dora_indicators" placeholder="例: 3s, 6z" v-model="formData.ura_dora_indicators">
          </div>
          <button type="button" @click="openModal" class="help-btn"> ？</button>
          <span>書き方</span>
        </fieldset>

        <fieldset>
          <legend>鳴き情報（副露）</legend>
          <div v-for="(meld, index) in formData.called_mentsu_list" :key="index" class="meld-group">
            <select v-model="meld.type" class="meld-type">
              <option value="pon">ポン</option>
              <option value="chi">チー</option>
              <option value="minkan">明槓</option>
              <option value="chakan">加槓</option>
            </select>
            <input type="text" v-model="meld.tiles" placeholder="例: 1m,1m,1m" class="meld-tiles">
            <button type="button" @click="removeMeld(index)" class="remove-btn">-</button>
          </div>
          <button type="button" @click="addMeld" class="add-btn">+ 鳴きを追加</button>
          
          <button type="button" @click="openModal" class="help-btn"> ？</button>
          <span>書き方</span>
        </fieldset>

        <fieldset>
          <legend>状況設定</legend>
          <div class="form-group">
            <label for="agari_hai">和了牌:</label>
            <input type="text" id="agari_hai" name="agarihai" placeholder="例: 5m, 2p" v-model="formData.agari_hai" required>
          </div>
          <div class="form-group">
            <label for="bakaze">場風:</label>
            <select id="bakaze" name="bakaze" v-model="formData.bakaze" required>
                <option value="1z">東</option>
                <option value="2z">南</option>
                <option value="3z">西</option>
                <option value="4z">北</option>
            </select>
          </div>
          <div class="form-group">
            <label for="jikaze">自風:</label>
            <select id="jikaze" name="jikaze" v-model="formData.jikaze" required>
                <option value="1z">東</option>
                <option value="2z">南</option>
                <option value="3z">西</option>
                <option value="4z">北</option>
            </select>
          </div>
          <div class="form-group">
            <label for="renchan">本場:</label>
            <input type="number" id="renchan" name="renchan" min="0" max="8" v-model="formData.renchan">
          </div>
          </fieldset>

        <fieldset>
          <legend>役の状況</legend>
          <div class="checkbox-grid">
            <div class="checkbox-item">
              <input type="checkbox" id="is_riichi" v-model="formData.is_riichi">
              <label for="is_riichi">立直</label>
            </div>
            <div class="checkbox-item">
              <input type="checkbox" id="is_double_riichi" v-model="formData.is_double_riichi">
              <label for="is_double_riichi">ダブル立直</label>
            </div>
            <div class="checkbox-item">
              <input type="checkbox" id="is_ippatsu" v-model="formData.is_ippatsu">
              <label for="is_ippatsu">一発</label>
            </div>
            <div class="checkbox-item">
              <input type="checkbox" id="is_haitei" v-model="formData.is_haitei">
              <label for="is_haitei">海底</label>
            </div>
            <div class="checkbox-item">
              <input type="checkbox" id="is_houtei" v-model="formData.is_houtei">
              <label for="is_houtei">河底</label>
            </div>
            <div class="checkbox-item">
              <input type="checkbox" id="is_rinshan" v-model="formData.is_rinshan">
              <label for="is_rinshan">嶺上開花</label>
            </div>
            <div class="checkbox-item">
              <input type="checkbox" id="is_chankan" v-model="formData.is_chankan">
              <label for="is_chankan">槍槓</label>
            </div>
            <div class="checkbox-item">
              <input type="checkbox" id="is_tenhou" v-model="formData.is_tenhou">
              <label for="is_tenhou">天和</label>
            </div>
            <div class="checkbox-item">
              <input type="checkbox" id="is_chiihou" v-model="formData.is_chiihou">
              <label for="is_chiihou">地和</label>
            </div>
          </div>
        </fieldset>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          {{ isLoading ? '計算中...' : '計算する' }}
        </button>
      </form>

      <div v-if="isLoading" class="loading-spinner">
        計算中...
      </div>
      
      <!-- エラーメッセージ -->
      <div v-if="errorState" class="error-message">
        <strong>エラー:</strong> {{ errorState }}
      </div>

      <!-- 点数計算結果 (エラーがなく、結果がある場合のみ表示) -->
      <ResultDisplay
        v-if="calculationResult && !errorState"
        :result="calculationResult"
      />

      <!-- 手牌表示 (手牌データが存在する場合に常に表示) -->
      <HandDisplay
        v-if="recognizedHand"
        :hand="recognizedHand"
        @recalculate="recalculateScore"
      />
      
    </main>

    <footer>
      <p>和了牌の画像は
        <a href="https://majandofu.com/mahjong-images" target="_blank" rel="noopener noreferrer">麻雀豆腐</a>
        様の素材を使用しています。
      </p>
    </footer>

    <!-- モーダルウィンドウ (変更なし) -->
    <div v-if="isModalVisible" class="modal-overlay" @click="closeModal">
      <!-- ( ... modal-content ... ) -->
      <div class="modal-content" @click.stop>
        <button class="close-btn" @click="closeModal">&times;</button>
        <h3>ドラ入力対応表</h3>
        <p>ドラ・裏ドラ・赤ドラの入力には、以下の形式を使用してください。</p>
        <table class="tile-table">
          <thead>
            <tr>
              <th>種類</th>
              <th>牌</th>
              <th>入力形式</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>マンズ</td>
              <td>🀇 ～ 🀏</td>
              <td><code>1m</code> ～ <code>9m</code></td>
            </tr>
            <tr>
              <td>ピンズ</td>
              <td>🀙 ～ 🀡</td>
              <td><code>1p</code> ～ <code>9p</code></td>
            </tr>
            <tr>
              <td>ソーズ</td>
              <td>🀐 ～ 🀘</td>
              <td><code>1s</code> ～ <code>9s</code></td>
            </tr>
            <tr>
              <td rowspan="7">字牌</td>
              <td>東</td>
              <td><code>1z</code></td>
            </tr>
            <tr>
              <td>南</td>
              <td><code>2z</code></td>
            </tr>
            <tr>
              <td>西</td>
              <td><code>3z</code></td>
            </tr>
            <tr>
              <td>北</td>
              <td><code>4z</code></td>
            </tr>
            <tr>
              <td>白</td>
              <td><code>5z</code></td>
            </tr>
            <tr>
              <td>發</td>
              <td><code>6z</code></td>
            </tr>
            <tr>
              <td>中</td>
              <td><code>7z</code></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

</template>

<style scoped>
/* App.vueのスタイルは変更なし */
/* ... (既存のスタイル) ... */
.container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: #f7f9f7;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #2c3e50;
}
header {
  text-align: center;
  margin-bottom: 2rem;
  border-bottom: 1px solid #dce5dc;
  padding-bottom: 1.5rem;
}
header h1 {
  font-size: 2.5rem;
  color: #004d40;
  margin: 0;
}
header p {
  font-size: 1.1rem;
  color: #556b55;
  margin-top: 0.5rem;
}
.score-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
fieldset {
  border: 1px solid #dce5dc;
  border-radius: 8px;
  padding: 1.5rem;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
legend {
  font-size: 1.3rem;
  font-weight: 600;
  padding: 0 0.75rem;
  color: #004d40;
  display: flex;
  align-items: center;
}
.form-group {
  display: grid;
  grid-template-columns: 150px 1fr;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}
.form-group:last-child {
  margin-bottom: 0;
}
.form-group label {
  font-weight: 500;
  text-align: right;
  padding-right: 1rem;
}
.form-group input[type="text"],
.form-group input[type="number"],
.form-group input[type="file"],
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s, box-shadow 0.3s;
}
.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #00796b;
  box-shadow: 0 0 0 3px rgba(0, 121, 107, 0.2);
}
.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
  padding-left: 160px;
}
.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.checkbox-item label {
  font-weight: normal;
  text-align: left;
}
.checkbox-item input[type="checkbox"] {
  width: 1.2em;
  height: 1.2em;
  accent-color: #004d40;
}
.submit-btn {
  display: block;
  width: 100%;
  padding: 1rem;
  font-size: 1.2rem;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(45deg, #004d40, #00796b);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-top: 1rem;
}
.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
.submit-btn:not(:disabled):hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 77, 64, 0.3);
}
.help-btn {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  width: 24px;
  height: 24px;
  margin-left: 8px;
  border: 1px solid #004d40;
  border-radius: 50%;
  background-color: #fff;
  color: #004d40;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;
}
.help-btn:hover {
  background-color: #004d40;
  color: #fff;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  width: 90%;
  max-width: 500px;
  position: relative;
}
.close-btn {
  position: absolute;
  top: 10px;
  right: 15px;
  border: none;
  background: none;
  font-size: 2rem;
  color: #aaa;
  cursor: pointer;
}
.close-btn:hover {
  color: #333;
}
.modal-content h3 {
  margin-top: 0;
  color: #004d40;
}
.tile-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
.tile-table th, .tile-table td {
  border: 1px solid #ddd;
  padding: 0.75rem;
  text-align: left;
}
.tile-table th {
  background-color: #f7f9f7;
}
.tile-table code {
  background-color: #e8f0e8;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}
.meld-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.meld-type {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
}
.meld-tiles {
  flex: 2;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
}
.add-btn, .remove-btn {
  padding: 0.5rem 0.75rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  background-color: #f0f0f0;
  cursor: pointer;
  font-weight: bold;
}
.add-btn {
  border-color: #00796b;
  color: #00796b;
  width: 100%;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  padding: 0.75rem;
}
.remove-btn {
  border-color: #d32f2f;
  color: #d32f2f;
}
.add-btn:hover {
  background-color: #e8f0e8;
}
.remove-btn:hover {
  background-color: #fbe9e7;
}
footer {
  text-align: center;
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid #dce5dc;
  font-size: 0.9rem;
  color: #556b55;
}
footer a {
  color: #00796b;
  text-decoration: none;
}
footer a:hover {
  text-decoration: underline;
}
/* ★★★ このスタイルを追加 ★★★ */
.loading-spinner {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: #004d40;
}
.error-message {
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: #fbe9e7;
  border: 1px solid #d32f2f;
  color: #d32f2f;
  border-radius: 8px;
  text-align: center;
}
</style>
