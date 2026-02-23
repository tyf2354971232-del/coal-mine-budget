import api from './index'

export const settlementApi = {
  overview() {
    return api.get('/settlement/overview')
  },
  civilList() {
    return api.get('/settlement/civil')
  },
  procurementMonthly() {
    return api.get('/settlement/procurement/monthly')
  },
  procurementRecords(params?: any) {
    return api.get('/settlement/procurement/records', { params })
  },
  procurementRecordsCount(params?: any) {
    return api.get('/settlement/procurement/records/count', { params })
  },
  procurementStats() {
    return api.get('/settlement/procurement/stats')
  },
  warehouseOutbound(params?: any) {
    return api.get('/settlement/warehouse/outbound', { params })
  },
  warehouseOutboundCount(params?: any) {
    return api.get('/settlement/warehouse/outbound/count', { params })
  },
  warehouseOutboundStats() {
    return api.get('/settlement/warehouse/outbound/stats')
  },
}
