<script setup>
import { ref } from 'vue';
// 送信データを定義.
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
  is_houtei: false,
  is_ippatsu: false,
  is_riichi: false,
  is_tenhou: false,
  is_chiihou: false,
  is_rinshan: false,
});
const sendData = () => {
  console.log("from data:", formData.value)
}
</script>

<template>
  <div>
    <header>
      
    </header>

    <main>
      <h1>麻雀得点計算サイト</h1>
      <p>このサイトでは、麻雀の得点計算を行うことができます。</p>
      <P>以下のフォームに手牌の画像とドラなどの情報を入力してください</P>
      <form @submit.prevent="sendData" method="post" enctype="multipart/form-data">
          <!-- <label for="image">手牌の画像:</label>
          <input type="file" id="image" name="image" accept="image/*" required><br><br> -->
          <!-- 和了り方 -->
          <label for="is_tsumo">和了り方:</label>
          <select id="is_tsumo" name="is_tsumo" v-model="formData.is_tsumo" required>
              <option value="true">ツモ</option>
              <option value="false">ロン</option>
          </select><br>
          <!-- 親子選択 -->
          <label for="is_oya">親/子:</label>
          <select id="is_oya" name="is_oya" v-model="formData.is_oya" required>
              <option value="true">親</option>
              <option value="false">子</option>
          </select><br>
          <!-- ドラの選択 -->
          <label for="dora_indicators">ドラ:</label>
          <input type="text" id="dora_indicators" name="dora_indicators" placeholder="例: 5m, 2p" v-model="formData.dora_indicators"><br>
          <!-- 裏ドラの選択 -->
          <label for="ura_dora_indicators">裏ドラ:</label>
          <input type="text" id="ura_dora_indicators" name="ura_dora_indicators" placeholder="例: 3s, 6z" v-model="formData.ura_dora_indicators"><br>
          <!-- 赤ドラの選択 -->
          <label for="aka_dora_indicators">赤ドラ:</label>
          <input type="text" id="aka_dora_indicators" name="aka_dora_indicators" placeholder="例: 5m, 2p" v-model="formData.aka_dora_indicators"><br>
          <!-- 場風の選択　-->
          <label for="bakaze">場風:</label>
          <select id="bakaze" name="bakaze" v-model="formData.bakaze" required>
              <option value="1z">東</option>
              <option value="2z">南</option>
              <option value="3z">西</option>
              <option value="4z">北</option>
          </select><br>
          <!-- 自風の選択 -->
          <label for="jikaze">自風:</label>
          <select id="jikaze" name="jikaze" v-model="formData.jikaze" required>
              <option value="1z">東</option>
              <option value="2z">南</option>
              <option value="3z">西</option>
              <option value="4z">北</option>
          </select><br>
          <!-- その他 -->
          <label for="renchan">連荘:</label>
          <input type="number" id="renchan" name="renchan" min="0" max="8" v-model="formData.renchan"><br>
          <label for="is_chankan">槍槓:</label>
          <input type="checkbox" id="is_chankan" name="is_chankan" v-model="formData.is_chankan"><br>
          <label for="is_haitei">海底:</label>
          <input type="checkbox" id="is_haitei" name="is_haitei" v-model="formData.is_haitei"><br>
          <label for="is_haitei">河底:</label>
          <input type="checkbox" id="is_houtei" name="is_houtei" v-model="formData.is_houtei"><br>
          <label for="is_ippatsu">一発:</label>
          <input type="checkbox" id="is_ippatsu" name="is_ippatsu" v-model="formData.is_ippatsu"><br>
          <label for="is_riichi">リーチ:</label>
          <input type="checkbox" id="is_riichi" name="is_riichi" v-model="formData.is_riichi"><br>
          <label for="is_tenhou">天和:</label>
          <input type="checkbox" id="is_tenhou" name="is_tenhou" v-model="formData.is_tenhou"><br>
          <label for="is_chiihou">地和:</label>
          <input type="checkbox" id="is_chiihou" name="is_chiihou" v-model="formData.is_chiihou"><br>
          <label for="is_rinshan">嶺上牌:</label>
          <input type="checkbox" id="is_rinshan" name="is_rinshan" v-model="formData.is_rinshan"><br>

          <input type="submit" value="計算する">
      </form>
    </main>
  </div>
</template>

<style scoped>
.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  /* header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  } */

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
