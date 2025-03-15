# **Guia de Implantação do Dermacam no Kubernetes**  

Este documento descreve os passos necessários para implantar o **Dermacam** em um cluster Kubernetes.  

---

## **1. Pré-requisitos**  

Antes de iniciar a implantação, certifique-se de que os seguintes itens estão instalados e configurados:  

- Um cluster Kubernetes funcional  
- `kubectl` instalado e configurado para se comunicar com o cluster  
- `kustomize` instalado (caso não esteja embutido no `kubectl`)  
- O **cert-manager** instalado para gerenciamento de certificados SSL  
- Um **Ingress Controller** funcional (`external-nginx` já configurado)  

---

## **2. Criar o Namespace**  

Antes de aplicar qualquer recurso, crie o namespace onde os componentes do **Dermacam** serão implantados:  

```sh
kubectl create namespace dermacam
```

Se o namespace já existir, este comando pode ser ignorado.  

---

## **3. Criar Secrets**  

As **Secrets** armazenam informações sensíveis, como credenciais do banco de dados, SMTP e MinIO.  

### **Arquivo: `kubernetes/secrets.yaml`**  

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: dermacam-secret
  namespace: dermacam
type: Opaque
data:
  ADMIN_NOME_INICIAL: <base64>
  ADMIN_EMAIL_INICIAL: <base64>
  ADMIN_CPF_INICIAL: <base64>
  ADMIN_SENHA_INICIAL: <base64>

  DB_USER: <base64>
  DB_PASSWORD: <base64>
  DB_HOST: <base64>
  DB_PORT: <base64>
  DB_NAME: <base64>

  MINIO_ENDPOINT: <base64>
  MINIO_ACCESS_KEY: <base64>
  MINIO_SECRET_KEY: <base64>
  MINIO_SECURE: <base64>

  SMTP_SERVER: <base64>
  SMTP_PORT: <base64>
  SMTP_USERNAME: <base64>
  SMTP_PASSWORD: <base64>
```

Todos os valores devem estar codificados em **Base64**. Para converter valores comuns para Base64, utilize o comando:

```sh
echo -n "valor" | base64
```

Exemplo para `DB_USER`:
```sh
echo -n "dermacam" | base64
```

Saída:
```
ZGVybWFjYW0=
```

Para decodificar um valor Base64:
```sh
echo "ZGVybWFjYW0=" | base64 --decode
```

### **Aplicação da Secret**  

```sh
kubectl apply -f kubernetes/secrets.yaml -n dermacam
```

---

## **4. Implantar os Recursos no Kubernetes**  

Todos os arquivos de configuração necessários já estão no diretório `kubernetes/`. Para aplicar tudo de uma vez usando **Kustomize**, execute:  

```sh
kubectl kustomize kubernetes/ | kubectl apply -f - -n dermacam
```

Isso criará automaticamente:  

- **Secrets**  
- **Services**  
- **Deployments**  
- **Ingress**  
- **Issuer do cert-manager**  

Para verificar se tudo foi implantado corretamente:  

```sh
kubectl get all -n dermacam
```

---

## **5. Acompanhar a Implantação**  

Após aplicar os manifests, monitore os pods para garantir que estejam rodando corretamente:  

```sh
kubectl get pods -n dermacam -w
```

Caso algum pod esteja em **CrashLoopBackOff** ou **Error**, veja os logs para identificar problemas:  

```sh
kubectl logs -n dermacam <nome-do-pod>
```

Se for necessário reiniciar o **Deployment**:  

```sh
kubectl rollout restart deployment dermacam-app -n dermacam
```

---

## **6. Verificar o Certificado SSL**  

Se a aplicação precisar de um certificado SSL via **Let's Encrypt**, o cert-manager estará gerenciando isso. Para verificar o status da emissão do certificado:  

```sh
kubectl get certificate -n dermacam
```

Se o certificado não for emitido corretamente, veja os eventos do cert-manager:  

```sh
kubectl describe certificate tls-dermacam -n dermacam
kubectl get challenges -n dermacam
```

Se precisar excluir e recriar o certificado:  

```sh
kubectl delete certificate tls-dermacam -n dermacam
kubectl delete order -n dermacam --all
kubectl delete challenge -n dermacam --all
kubectl apply -f kubernetes/issuer.yaml -n dermacam
```

---

## **7. Alterando o Domínio no Ingress**  

Se for necessário trocar o domínio do **Ingress**, edite o arquivo `kubernetes/ingress.yaml`, alterando a linha:  

```yaml
host: arthrok.shop
```

Para o novo domínio desejado.  

Após a alteração, reaplique o `Ingress`:  

```sh
kubectl apply -f kubernetes/ingress.yaml -n dermacam
kubectl rollout restart deployment dermacam-app -n dermacam
```

Para verificar se o Ingress está funcionando corretamente:  

```sh
kubectl get ingress -n dermacam
kubectl describe ingress ingress-dermacam -n dermacam
```

Se houver erro **502 Bad Gateway**, pode ser que o serviço ainda não esteja acessível. Confirme se os endpoints estão corretamente configurados:  

```sh
kubectl get endpoints dermacam-service -n dermacam
```