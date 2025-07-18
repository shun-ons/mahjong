<template>
  <div id="mahjong-app">
    <header>
      <h1>麻雀得点計算サイト</h1>
      <p>このサイトでは、麻雀の得点計算を行うことができます。<br>以下のフォームに手牌の画像と情報を入力してください。</p>
    </header>

    <main>
      <form @submit.prevent="calculateScore" class="score-form">
        
        <fieldset>
          <legend>基本情報</legend>
          <div class="form-group">
            <label for="image">手牌の画像:</label>
            <input type="file" id="image" @change="handleFileUpload" accept="image/*" required>
          </div>
          <div class="form-group">
            <label for="is_oya">親/子:</label>
            <select id="is_oya" v-model="formData.is_oya" required>
              <option :value="true">親</option>
              <option :value="false">子</option>
            </select>
          </div>
          <div class="form-group">
            <label for="is_tsumo">和了り方:</label>
            <select id="is_tsumo" v-model="formData.is_tsumo" required>
              <option :value="true">ツモ</option>
              <option :value="false">ロン</option>
            </select>
          </div>
        </fieldset>

        <fieldset>
          <legend>ドラ情報</legend>
          <div class="form-group">
            <label for="dora_indicators">ドラ:</label>
            <input type="text" id="dora_indicators" v-model="formData.dora_indicators" placeholder="例: 5m, 2p">
          </div>
          <div class="form-group">
            <label for="ura_dora_indicators">裏ドラ:</label>
            <input type="text" id="ura_dora_indicators" v-model="formData.ura_dora_indicators" placeholder="例: 3s, 6z">
          </div>
          <div class="form-group">
            <label for="aka_dora_indicators">赤ドラ:</label>
            <input type="text" id="aka_dora_indicators" v-model="formData.aka_dora_indicators" placeholder="例: 5m, 2p">
          </div>
        </fieldset>

        <fieldset>
          <legend>状況設定</legend>
          <div class="form-group">
            <label for="bakaze">場風:</label>
            <select id="bakaze" v-model="formData.bakaze" required>
              <option value="1z">東</option>
              <option value="2z">南</option>
              <option value="3z">西</option>
              <option value="4z">北</option>
            </select>
          </div>
          <div class="form-group">
            <label for="jikaze">自風:</label>
            <select id="jikaze" v-model="formData.jikaze" required>
              <option value="1z">東</option>
              <option value="2z">南</option>
              <option value="3z">西</option>
              <option value="4z">北</option>
            </select>
          </div>
          <div class="form-group">
            <label for="renchan">本場:</label>
            <input type="number" id="renchan" v-model.number="formData.renchan" min="0" max="8">
          </div>
        </fieldset>

        <fieldset>
          <legend>役の状況（該当する場合にチェック）</legend>
          <div class="checkbox-grid">
            <div class="checkbox-item">
              <input type="checkbox" id="is_riichi" v-model="formData.is_riichi">
              <label for="is_riichi">リーチ</label>
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
              <input type="checkbox" id="is_kaitei" v-model="formData.is_kaitei">
              <label for="is_kaitei">河底</label>
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

        <button type="submit" class="submit-btn">計算する</button>
      </form>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// refを使って、フォームの各入力値をリアクティブなデータとして管理
const formData = ref({
  image: null,
  is_tsumo: true,
  is_oya: false,
  dora_indicators: '',
  ura_dora_indicators: '',
  aka_dora_indicators: '',
  bakaze: '1z',
  jikaze: '1z',
  renchan: 0,
  is_chankan: false,
  is_haitei: false,
  is_kaitei: false,
  is_ippatsu: false,
  is_riichi: false,
  is_tenhou: false,
  is_chiihou: false,
  is_rinshan: false,
});

// ファイルが選択されたときに呼ばれるメソッド
const handleFileUpload = (event) => {
  // 選択されたファイルをformDataに格納
  formData.value.image = event.target.files[0];
};

// フォームが送信されたときに呼ばれるメソッド
const calculateScore = () => {
  // FormDataオブジェクトを作成して、ファイルと他のデータをひとまとめにする
  const submissionData = new FormData();
  
  // formDataの各キーと値をsubmissionDataに追加
  for (const key in formData.value) {
    submissionData.append(key, formData.value[key]);
  }

  // ここでサーバーにデータを送信する
  console.log('以下のデータがサーバーに送信されます:');
  for (let [key, value] of submissionData.entries()) {
    console.log(`${key}:`, value);
  }

  /*
  // 実際のAPI通信の例
  fetch('/api/calculate', {
    method: 'POST',
    body: submissionData,
  })
  .then(response => response.json())
  .then(result => {
    console.log('計算結果:', result);
    // ここで計算結果を画面に表示する処理などを行う
  })
  .catch(error => {
    console.error('エラーが発生しました:', error);
  });
  */
};
</script>

<style scoped>
/* 全体のスタイル */
#mahjong-app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: #f9f9f9;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  color: #333;
}

header {
  text-align: center;
  margin-bottom: 2rem;
}

header h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

/* フォームのスタイル */
.score-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

fieldset {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1.5rem;
  background-color: #fff;
}

legend {
  font-size: 1.2rem;
  font-weight: 600;
  padding: 0 0.5rem;
  color: #2c3e50;
}

.form-group {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}
.form-group:last-child {
    margin-bottom: 0;
}

.form-group label {
  flex: 1;
  font-weight: 500;
  margin-right: 1rem;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group input[type="file"],
.form-group select {
  flex: 2;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.2);
}

/* チェックボックスのグリッドレイアウト */
.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-item input[type="checkbox"] {
  width: 1.2em;
  height: 1.2em;
}


/* 送信ボタン */
.submit-btn {
  display: block;
  width: 100%;
  padding: 1rem;
  font-size: 1.2rem;
  font-weight: 600;
  color: #fff;
  background-color: #42b983;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover {
  background-color: #36a473;
}
</style>