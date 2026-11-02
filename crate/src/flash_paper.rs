//! Minimal, venue-independent Flash Paper lifecycle core.
//!
//! The core deliberately stores no balance. A position mints exposure on open
//! and burns it on close; the only durable output is an append-only event log.

#[derive(Debug, Clone, PartialEq)]
pub struct Position { pub id: u64, pub limit: u64, pub opened_at: u64 }

#[derive(Debug, Clone, PartialEq)]
pub enum Event {
    Opened { id: u64, limit: u64, timestamp: u64 },
    Closed { id: u64, proceeds: u64, fee: u64, timestamp: u64 },
}

#[derive(Debug, Default)]
pub struct Simulator { next_id: u64, open: Option<Position>, events: Vec<Event> }

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Error { PositionAlreadyOpen, NoOpenPosition, InvalidFeeBps }

impl Simulator {
    pub fn open(&mut self, limit: u64, timestamp: u64) -> Result<Position, Error> {
        if self.open.is_some() { return Err(Error::PositionAlreadyOpen); }
        let position = Position { id: self.next_id, limit, opened_at: timestamp };
        self.next_id += 1;
        self.events.push(Event::Opened { id: position.id, limit, timestamp });
        self.open = Some(position.clone());
        Ok(position)
    }

    pub fn close(&mut self, proceeds: u64, fee_bps: u16, timestamp: u64) -> Result<u64, Error> {
        if fee_bps > 10_000 { return Err(Error::InvalidFeeBps); }
        let position = self.open.take().ok_or(Error::NoOpenPosition)?;
        let fee = proceeds.saturating_mul(fee_bps as u64) / 10_000;
        self.events.push(Event::Closed { id: position.id, proceeds, fee, timestamp });
        Ok(proceeds - fee)
    }

    pub fn open_position(&self) -> Option<&Position> { self.open.as_ref() }
    pub fn events(&self) -> &[Event] { &self.events }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn flash_money_mints_then_burns_without_balance() {
        let mut sim = Simulator::default();
        let p = sim.open(800_000, 1).unwrap();
        assert_eq!(p.limit, 800_000);
        assert_eq!(sim.close(900_000, 200, 2).unwrap(), 882_000);
        assert!(sim.open_position().is_none());
        assert_eq!(sim.events().len(), 2);
    }
    #[test]
    fn lifecycle_rejects_double_open_and_close_without_position() {
        let mut sim = Simulator::default();
        sim.open(1, 1).unwrap();
        assert_eq!(sim.open(2, 2), Err(Error::PositionAlreadyOpen));
        sim.close(1, 0, 2).unwrap();
        assert_eq!(sim.close(1, 0, 3), Err(Error::NoOpenPosition));
    }
}
